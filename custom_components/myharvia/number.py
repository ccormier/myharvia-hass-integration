"""Platform for myharvia switch integration."""
from __future__ import annotations

from typing import cast

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
    NumberEntityDescription,
)

from homeassistant.const import UnitOfTemperature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MyHarviaEntity

ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="targetTemp",
        name="Target Temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=40,
        native_max_value=90,
        native_step=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the number platform."""
    async_add_entities(
        MyHarviaNumber(coordinator=coordinator, entity_description=entity_description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MyHarviaNumber(MyHarviaEntity, NumberEntity):
    """MyHarvia Number class."""

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        return cast(float, self._device.get_reported_state(self.entity_description.key))

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        data = {self.entity_description.key: value}
        await self._device.async_request_state_change(data)
        await self.coordinator.async_request_refresh()
