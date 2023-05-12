"""Platform for myharvia switch integration."""
from __future__ import annotations

from typing import Any, cast

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .entity import MyHarviaEntity

ENTITY_DESCRIPTIONS: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="light",
        name="Light",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:lightbulb",
    ),
    SwitchEntityDescription(
        key="fan",
        name="Fan",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:fan",
    ),
    SwitchEntityDescription(
        key="active",
        name="Heater",
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:heat-wave",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        MyHarviaSwitch(coordinator=coordinator, entity_description=entity_description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MyHarviaSwitch(MyHarviaEntity, SwitchEntity):
    """MyHarvia Switch class."""

    @property
    def is_on(self) -> bool | None:
        return cast(bool, self._device.get_reported_state(self.entity_description.key))

    async def async_turn_on(self, **kwargs: Any) -> None:
        data = {self.entity_description.key: 1}
        await self._device.async_request_state_change(data)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        data = {self.entity_description.key: 0}
        await self._device.async_request_state_change(data)
        await self.coordinator.async_request_refresh()
