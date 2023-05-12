"""DataUpdateCoordinator for MyHarvia component."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    MyHarviaDevice,
    MyHarviaAuthenticationFailed,
    MyHarviaApiClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MyHarviaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        device: MyHarviaDevice,
    ) -> None:
        """Initialize."""
        self.device = device
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.device.async_update()
            return {}
        except MyHarviaAuthenticationFailed as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MyHarviaApiClientError as exception:
            raise UpdateFailed(exception) from exception
