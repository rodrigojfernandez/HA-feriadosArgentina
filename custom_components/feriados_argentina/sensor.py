"""Sensors for Feriados Argentina."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ArgentinaHolidaysCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: ArgentinaHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TodayHolidaySensor(coordinator)])


class TodayHolidaySensor(CoordinatorEntity, SensorEntity):
    """Sensor showing today's holiday name(s)."""

    _attr_name = "Today's Holiday"
    _attr_unique_id = "feriados_argentina_today_holiday"
    _attr_icon = "mdi:calendar-text"

    def __init__(self, coordinator: ArgentinaHolidaysCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "feriados_argentina")},
            "name": "Holiday Days Argentina",
            "manufacturer": "ArgentinaDatos API",
            "model": "National Holidays",
        }

    @property
    def native_value(self) -> str:
        """Return the holiday name or a default message."""
        today_all = self.coordinator.data.get("today_all", [])
        if not today_all:
            return "Not a holiday or non-working day"
        names = _unique([h["name"] for h in today_all if h["name"]])
        return ", ".join(names) if names else "Holiday"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        today = self.coordinator.data.get("today")
        today_holidays = self.coordinator.data.get("today_holidays", [])
        today_non_working = self.coordinator.data.get("today_non_working_days", [])

        attrs: dict = {
            "year": today.year if today else None,
            "date": today.isoformat() if today else None,
            "is_holiday": bool(today_holidays),
            "is_non_working_day": bool(today_non_working),
        }

        if today_holidays:
            attrs["holidays"] = [{"name": h["name"], "type": h["type"]} for h in today_holidays]
        if today_non_working:
            attrs["non_working_days"] = [
                {"name": h["name"], "type": h["type"]} for h in today_non_working
            ]

        return attrs


def _unique(lst: list[str]) -> list[str]:
    """Return unique items preserving order."""
    seen: set = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
