"""Feriados Argentina integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_INCLUDE_ISLAMIC, CONF_INCLUDE_JEWISH, DOMAIN
from .coordinator import ArgentinaHolidaysCoordinator

PLATFORMS = ["binary_sensor", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Feriados Argentina from a config entry."""
    include_jewish = entry.options.get(
        CONF_INCLUDE_JEWISH, entry.data.get(CONF_INCLUDE_JEWISH, False)
    )
    include_islamic = entry.options.get(
        CONF_INCLUDE_ISLAMIC, entry.data.get(CONF_INCLUDE_ISLAMIC, False)
    )

    coordinator = ArgentinaHolidaysCoordinator(hass, include_jewish, include_islamic)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update — reload to apply new preferences."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
