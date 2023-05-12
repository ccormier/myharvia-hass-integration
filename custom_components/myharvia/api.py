"""Library to talk use MyHarvia API."""
from __future__ import annotations

import json
import aiohttp
from pycognito import Cognito
from pycognito.exceptions import WarrantException
from homeassistant.core import HomeAssistant

from .const import LOGGER


class MyHarviaAuthenticationFailed(Exception):
    """Authentication Exception."""


class MyHarviaServiceDescriptionFailure(Exception):
    """Failed to retrieve Service Description Exception."""


class MyHarviaApiClientError(Exception):
    """Failed to retrieve Service Description Exception."""


class MyHarviaApi:
    """Initialize and Return an MyHarvia API Client."""

    def __init__(
        self,
        username: str = None,
        password: str = None,
        token_file="myharvia_token.json",
        hass: HomeAssistant = None,
        session=None,
    ):
        """Create MyHarviaAPI Client."""
        self.username = username
        self.password = password
        self.token_file = token_file
        self.hass = hass
        self.session = session
        self.cognito = None
        self.headers = None
        self.config: dict = {}

    async def async_init(self) -> None:
        """Async init, retrieve and store service description, authenticate."""
        self.config["user"] = await self._get_harvia_config("users")
        self.config["device"] = await self._get_harvia_config("device")
        self.config["data"] = await self._get_harvia_config("data")
        self.config["events"] = await self._get_harvia_config("events")
        await self.authenticate()

    def _blocked_cognito_auth(self) -> None:
        self.cognito = Cognito(
            self.config["user"]["userPoolId"],
            self.config["user"]["clientId"],
            username=self.username,
        )

    async def _authenticate_with_pass(self) -> None:
        """Authenicate with password."""
        try:
            await self.hass.async_add_executor_job(
                self.cognito.authenticate, self.password
            )
            # self.cognito.authenticate(self.password)
        except Exception as exc:
            raise MyHarviaAuthenticationFailed(
                "Failed to authenticate with the provided username and password."
            ) from exc
        access_token_data = {
            "access_token": self.cognito.access_token,
            "id_token": self.cognito.id_token,
            "refresh_token": self.cognito.refresh_token,
        }
        with open(self.token_file, "w", encoding="utf-8") as file:
            json.dump(access_token_data, file)
        LOGGER.debug("Authentication successful using username and password.")

    async def authenticate(self) -> None:
        """Authenticate to cognito service."""
        if self.cognito is not None:
            try:
                await self.hass.async_add_executor_job(self.cognito.check_token)
            except WarrantException:
                await self._authenticate_with_pass()
        else:
            LOGGER.debug("Entering _blocked_auth")
            await self.hass.async_add_executor_job(self._blocked_cognito_auth)
            LOGGER.debug("done _blocked_auth: %s", self.cognito)

            # Try to load access token, user_pool_id, and client_id from file
            try:
                with open(self.token_file, encoding="utf-8") as file:
                    access_token_data = json.load(file)
                    self.cognito.access_token = access_token_data["access_token"]
                    self.cognito.id_token = access_token_data["id_token"]
                    self.cognito.refresh_token = access_token_data["refresh_token"]
                    await self.hass.async_add_executor_job(self.cognito.check_token)
                    # self.cognito.check_token()
                LOGGER.debug("Authentication successful using stored tokens.")
            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
                await self._authenticate_with_pass()

        self.headers = {
            "Authorization": f"Bearer {self.cognito.id_token}",
            "Content-Type": "application/json",
        }

    async def get_config_device(self) -> dict:
        """Return config service description."""
        return self.config["device"]

    async def get_config_data(self) -> dict:
        """Return data service description."""
        return self.config["data"]

    async def _get_harvia_config(self, service) -> dict:
        url = f"https://prod.myharvia-cloud.net/{service}/endpoint"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    config_data = await response.json()
                    return config_data
                else:
                    raise MyHarviaServiceDescriptionFailure(
                        f"Failed to get configuration data. Status code: {response.status}"
                    )

    async def send_request(self, api_base_url, data, retry=True):
        """Post request to api and return results as a dict."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(api_base_url, json=data) as response:
                if response.status == 401 and retry:  # Token expired
                    await self.authenticate()
                    return await self.send_request(api_base_url, data, retry=False)
                if response.status not in (200, 201):
                    raise MyHarviaApiClientError(
                        f"API request failed with status code {response.status}: {response.text}"
                    )
                return await response.json()

    async def get_devices(self):
        """Return a list of Devices."""
        data = {
            "operationName": "Query",
            "variables": {},
            "query": """query Query {
                getDeviceTree
            }
            """,
        }
        await self.async_init()
        LOGGER.debug("config_device: %s", self.config["device"])
        r = await self.send_request(self.config["device"]["endpoint"], data)
        device_tree = json.loads(r["data"]["getDeviceTree"])
        devices = []
        for x in device_tree:
            if "c" in x and x["c"]:
                devices.extend(c["i"]["name"] for c in x["c"])

        return devices


class MyHarviaDevice:
    """Initialize and Return a MyHarvia Device object."""

    def __init__(self, myharvia_api: MyHarviaApi, device_id: str):
        """Create MyHarviaDevice object."""
        self.myharvia_api = myharvia_api
        self.device_id = device_id
        self.display_name = None
        self.type = None
        self.model = None
        self.sw_version = None
        self.hw_version = None
        self.data = None
        self.state = None
        self.api_device_url = None
        self.api_data_url = None

    async def async_init(self) -> None:
        """Async Initialize MyHarviaDevice."""
        self.api_device_url = (await self.myharvia_api.get_config_device())["endpoint"]
        self.api_data_url = (await self.myharvia_api.get_config_data())["endpoint"]
        self.state = await self.async_get_state()
        self.data = await self.async_get_data()
        self.type = self.data["getLatestData"]["type"]
        self.display_name = self.get_reported_state("displayName")
        self.model = self.get_reported_state("devType")
        self.sw_version = self.get_reported_state("swVer")
        self.hw_version = self.get_reported_state("hwVer")

    def get_latest_data(self, key: str):
        """Return value from self data.getLatestData.data.key."""
        return self.data["getLatestData"]["data"][key]

    def get_reported_state(self, key: str):
        """Return value from self state.getDeviceState.reported.key."""
        return self.state["getDeviceState"]["reported"][key]

    async def async_update(self, data: bool = True, state: bool = True) -> None:
        """Pull latest data from API and update object."""
        if data:
            self.data = await self.async_get_data()
        if state:
            self.state = await self.async_get_state()

    async def async_dump_data(self) -> dict:
        """Return instance data."""
        return self.data

    async def async_get_data(self) -> dict:
        """Query device data from API."""
        data = {
            "operationName": "Query",
            "variables": {
                "deviceId": self.device_id,
            },
            "query": """query Query($deviceId: String!) {
            getLatestData(deviceId: $deviceId) {
                deviceId
                timestamp
                sessionId
                type
                data
                __typename
            }
            }""",
        }
        response = await self.myharvia_api.send_request(self.api_data_url, data)
        device_data = response["data"]
        # Load remaining json data
        device_data["getLatestData"]["data"] = json.loads(
            device_data["getLatestData"]["data"]
        )
        return device_data

    async def async_get_state(self) -> dict:
        """Query device state from API."""
        data = {
            "operationName": "Query",
            "variables": {
                "deviceId": self.device_id,
            },
            "query": """query Query($deviceId: ID!) {
                getDeviceState(deviceId: $deviceId) {
                    desired
                    reported
                    timestamp
                    __typename
                }
            }""",
        }
        response = await self.myharvia_api.send_request(self.api_device_url, data)
        device_state = response["data"]
        device_state["getDeviceState"]["reported"] = json.loads(
            device_state["getDeviceState"]["reported"]
        )
        device_state["getDeviceState"]["desired"] = json.loads(
            device_state["getDeviceState"]["desired"]
        )
        return device_state

    async def async_request_state_change(
        self, state_data: dict, operation_name: str = "Mutation"
    ) -> dict:
        """Post state change request to API."""
        state_data_json = json.dumps(state_data)
        data = {
            "operationName": operation_name,
            "variables": {
                "deviceId": self.device_id,
                "state": state_data_json,
                "getFullState": False,
            },
            "query": """mutation Mutation($deviceId: ID!, $state: AWSJSON!, $getFullState: Boolean) {
                requestStateChange(deviceId: $deviceId, state: $state, getFullState: $getFullState)
            }""",
        }
        response = await self.myharvia_api.send_request(self.api_device_url, data)
        return response["data"]
