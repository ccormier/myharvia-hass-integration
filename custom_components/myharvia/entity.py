"""MyHarviaEntity class."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityDescription

from .const import ATTRIBUTION, DOMAIN
from .coordinator import MyHarviaDataUpdateCoordinator
from .api import MyHarviaDevice


class MyHarviaEntity(CoordinatorEntity[MyHarviaDataUpdateCoordinator]):
    """MyHarviaEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MyHarviaDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.device_id}_{entity_description.key}"
        self._attr_name = (
            f"{str(coordinator.device.type).capitalize()} {entity_description.name}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device.device_id)},
            name=coordinator.device.display_name,
            model=coordinator.device.model,
            sw_version=coordinator.device.sw_version,
            hw_version=coordinator.device.hw_version,
        )
        self.entity_description = entity_description

    @property
    def _device(self) -> MyHarviaDevice:
        """Return the device."""
        return self.coordinator.device

    @property
    def device_id(self) -> str:
        """Return the device id of the MyHarvia device."""
        return self.coordinator.device.device_id
