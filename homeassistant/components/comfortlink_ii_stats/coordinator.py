"""Example integration using DataUpdateCoordinator."""

import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ComfortLinkCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config_entry):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
        )
        self.compressor_speed = None        

	# coordinator.async_set_updated_data(data)

    def async_set_compressor_speed(self, compressor_speed):
        self.compressor_speed = compressor_speed
        self.async_set_updated_data(self.compressor_speed)

    async def async_update_data(self):
        # This function will be called periodically according to the configured update interval
        # You can perform any necessary tasks here, if required
        pass

