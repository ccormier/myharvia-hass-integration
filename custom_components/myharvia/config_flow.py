"""Adds config flow for MyHarvia component."""
from __future__ import annotations

from typing import Any, Dict, Optional
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from .api import MyHarviaApi

from .const import DOMAIN, LOGGER


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """MyHarvia config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        errors = {}

        if user_input is not None:
            try:
                harvia_service = MyHarviaApi(
                    username=user_input["username"],
                    password=user_input["password"],
                )

                await self.async_set_unique_id(harvia_service.username)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["username"], data=user_input
                )
            except Exception as exc:
                LOGGER.error("Failed to connect to Harvia service: %s", exc)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_user_schema(),
            errors=errors,
        )

    @staticmethod
    def _get_user_schema() -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )
