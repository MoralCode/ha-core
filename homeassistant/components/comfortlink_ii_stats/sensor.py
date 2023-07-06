"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, MAC_ADDR
from .coordinator import ComfortLinkCoordinator


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # add_entities([ComfortLink2Sensor()])
    # get coordinator
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(
        ComfortLink2Sensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    print("setup entry")

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        ComfortLink2Sensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class ComfortLink2Sensor(ComfortLinkCoordinator, SensorEntity):
    """Representation of a Sensor using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _attr_name = "ComfortLink 2"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.POWER_FACTOR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self.coordinator = coordinator

    @property
    def unique_id(self):
        return MAC_ADDR

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, MAC_ADDR)
            },
            name=self.name,
            manufacturer="Trane, Inc.",
            model="XL850",
            sw_version="0.0.0",
            # via_device=(DOMAIN, self.api.bridgeid),
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()
