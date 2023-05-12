"""Sensor platform for MyHarvia."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import (
    UnitOfTemperature,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    # EntityCategory,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .entity import MyHarviaEntity
from .api import MyHarviaDevice


@dataclass
class MyHarviaSensorEntityDescriptionMixIn:
    """Mixin for MyHarvia sensor."""

    value_fn: Callable[[MyHarviaDevice], StateType | datetime]


@dataclass
class MyHarviaSensorEntityDescription(
    SensorEntityDescription, MyHarviaSensorEntityDescriptionMixIn
):
    """Class to describe a MyHarvia sensor."""


ENTITY_DESCRIPTIONS: tuple[MyHarviaSensorEntityDescription, ...] = (
    MyHarviaSensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.get_latest_data("temperature"),
    ),
    MyHarviaSensorEntityDescription(
        key="wifi",
        name="Signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        # entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        value_fn=lambda device: device.get_latest_data("wifiRSSI"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        MyHarviaSensor(coordinator=coordinator, entity_description=entity_description)
        for coordinator in hass.data[DOMAIN][entry.entry_id]
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MyHarviaSensor(MyHarviaEntity, SensorEntity):
    """MyHarvia Sensor class."""

    entity_description: MyHarviaSensorEntityDescription

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        # temperature at ['data']['temperature']
        # return self.coordinator.data.get("temperature")
        return self.entity_description.value_fn(self._device)
