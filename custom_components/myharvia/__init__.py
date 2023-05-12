"""Custom integration to integrate MyHarvia cloud service with Home Assistant.

For more details about this integration, please refer to
https://github.com/ccormier/myharvia-hass-integration
"""
from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .api import MyHarviaApi, MyHarviaDevice
from .const import DOMAIN
from .coordinator import MyHarviaDataUpdateCoordinator


PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyHarvia from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = MyHarviaApi(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        hass=hass,
    )

    await client.async_init()

    devices: list[MyHarviaDevice] = await client.get_devices()

    device_coordinators: list[MyHarviaDataUpdateCoordinator] = []
    for device in devices:
        device = MyHarviaDevice(client, device)
        await device.async_init()
        device_coordinator = MyHarviaDataUpdateCoordinator(hass, device)
        device_coordinators.append(device_coordinator)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device_coordinators

    await asyncio.gather(
        *[
            coordinator.async_config_entry_first_refresh()
            for coordinator in device_coordinators
        ]
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
