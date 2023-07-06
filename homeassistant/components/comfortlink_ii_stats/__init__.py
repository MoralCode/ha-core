"""The Comfortlink 2 Stats integration."""
from __future__ import annotations

from lantrane import Trane

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_HOST, CONF_PORT, DOMAIN

from .coordinator import ComfortLinkCoordinator

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Comfortlink 2 Stats from a config entry."""

    trane = Trane(entry.data[CONF_HOST], entry.data[CONF_PORT])

    if not await hass.async_add_executor_job(trane.validate):
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {"trane_client": trane}


    coordinator = ComfortLinkCoordinator(hass, entry)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    # Start the socket connection and data processing in a separate thread or asyncio task
    threading.Thread(target=start_socket_connection, args=(hass, coordinator)).start()
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async_add_entities(
        ComfortLink2Sensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )

    return True

def start_socket_connection(hass, coordinator, trane):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(socket_listener(hass, coordinator, trane))
    loop.close()

async def socket_listener(hass, coordinator, trane):
    # Create a socket connection to your device and listen for data
    # Use your Python library to process the received raw bytes into a class
    # Update the coordinator with the new compressor speed value whenever it changes
    # Example:
    # for data in trane.listen():
    while True:
        raw_data = await my_device.receive_data()
        compressor_speed = my_device.process_data(raw_data)
        coordinator.async_set_compressor_speed(compressor_speed)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
