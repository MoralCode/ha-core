"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, MAC_ADDR
from .coordinator import ComfortLinkCoordinator
from lantrane import Trane


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    """ perform the setup for this platform"""

    registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    entity_id = er.async_validate_entity_id(registry, entry.entry_id)
    # TODO Optionally validate config entry options before creating entity
    name = entry.title
    unique_id = entry.entry_id

    trane = hass.data[DOMAIN][entry.entry_id]["trane_client"]
    async_add_entities([ComfortLink2Sensor(unique_id, name, entity_id, trane)])

    # async_add_entities(
    #     ComfortLink2Sensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    # )


class ComfortLink2Sensor(SensorEntity):
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
    # _attr_unique_id = MAC_ADDR

    def __init__(self, unique_id: str, name: str, wrapped_entity_id: str, clientlib: Trane) -> None:
        """Initialize NEW_DOMAIN Sensor."""
        super().__init__()
        self._wrapped_entity_id = wrapped_entity_id
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._clientlib = clientlib
        self._unsub = lambda a: a


    async def async_added_to_hass(self) -> None:
        """Subscribe to data updates."""
        self._unsub = await self.hass.async_add_executor_job(
            self._clientlib.on_data,# add a callback to listen for new data
            self._update_data,
        )

        self.hass.data[DOMAIN].entity_ids.add(self.entity_id)


        return

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from data updates."""
        await self.hass.async_add_executor_job(self._unsub)

    def _update_data(self, data):
        """ Tell HomeAssistant that new data is available"""
        hass.states.set(DOMAIN + ".compressor_speed", data.cmp_spd)
        # self.state.native_value
        self.async_schedule_update_ha_state()
    
    # def __init__(self, coordinator, idx):
    #     """Pass coordinator to CoordinatorEntity."""
    #     super().__init__(coordinator, context=idx)
    #     self.idx = idx
    #     self.coordinator = coordinator

    # @property
    # def unique_id(self):
    #     return self.idx

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
