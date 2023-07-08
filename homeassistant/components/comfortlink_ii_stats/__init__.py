"""The Comfortlink 2 Stats integration."""
from __future__ import annotations

import asyncio
import threading

from lantrane import Trane

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_HOST, CONF_PORT, DOMAIN

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Comfortlink 2 Stats from a config entry."""

    trane = Trane(entry.data[CONF_HOST], entry.data[CONF_PORT])

    if not await hass.async_add_executor_job(trane.validate):
        raise ConfigEntryNotReady(
            "invalid credentials - could not connect to Comfortlink"
        )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"trane_client": trane}


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
