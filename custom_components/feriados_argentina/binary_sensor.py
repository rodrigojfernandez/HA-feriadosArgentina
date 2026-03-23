"""Binary sensors for Feriados Argentina."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up binary sensor entities."""
    coordinator: ArgentinaHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            IsHolidayTodayBinarySensor(coordinator),
            IsNonWorkingDayTodayBinarySensor(coordinator),
        ]
    )


class _BaseArgentinaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class with shared device info."""

    def __init__(self, coordinator: ArgentinaHolidaysCoordinator) -> None:
        """Initialize the binary sensor."""
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


class IsHolidayTodayBinarySensor(_BaseArgentinaBinarySensor):
    """Binary sensor that is on when today is an official holiday."""

    _attr_name = "Is Holiday Today"
    _attr_unique_id = "feriados_argentina_is_holiday"
    _attr_icon = "mdi:calendar-star"

    @property
    def is_on(self) -> bool:
        """Return true if today is an official holiday."""
        return bool(self.coordinator.data.get("today_holidays"))

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        holidays = self.coordinator.data.get("today_holidays", [])
        today = self.coordinator.data.get("today")
        attrs: dict = {
            "year": today.year if today else None,
            "date": today.isoformat() if today else None,
        }
        if holidays:
            attrs["name"] = ", ".join(_unique([h["name"] for h in holidays]))
            attrs["type"] = ", ".join(_unique([h["type"] for h in holidays]))
            attrs["holidays"] = holidays
        return attrs


class IsNonWorkingDayTodayBinarySensor(_BaseArgentinaBinarySensor):
    """Binary sensor that is on when today is a non-working day (bridge day)."""

    _attr_name = "Is Non-Working Day Today"
    _attr_unique_id = "feriados_argentina_is_non_working_day"
    _attr_icon = "mdi:calendar-remove"

    @property
    def is_on(self) -> bool:
        """Return true if today is a non-working day."""
        return bool(self.coordinator.data.get("today_non_working_days"))

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        non_working = self.coordinator.data.get("today_non_working_days", [])
        today = self.coordinator.data.get("today")
        attrs: dict = {
            "year": today.year if today else None,
            "date": today.isoformat() if today else None,
        }
        if non_working:
            attrs["name"] = ", ".join(_unique([h["name"] for h in non_working]))
            attrs["type"] = ", ".join(_unique([h["type"] for h in non_working]))
            attrs["non_working_days"] = non_working
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
