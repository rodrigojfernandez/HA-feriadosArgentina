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
    coordinator: ArgentinaHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FeriadoNombreSensor(coordinator)])


class FeriadoNombreSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing today's holiday name(s)."""

    _attr_name = "Feriado de hoy"
    _attr_unique_id = "feriados_argentina_nombre"
    _attr_icon = "mdi:calendar-text"

    def __init__(self, coordinator: ArgentinaHolidaysCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "feriados_argentina")},
            "name": "Feriados Argentina",
            "manufacturer": "Argentina.gob.ar",
            "model": "Feriados Nacionales",
        }

    @property
    def native_value(self) -> str:
        today_holidays = self.coordinator.data.get("today_holidays", [])
        if not today_holidays:
            return "No es feriado ni día no laborable"
        names = _unique([h["name"] for h in today_holidays if h["name"]])
        return ", ".join(names) if names else "Feriado"

    @property
    def extra_state_attributes(self) -> dict:
        today = self.coordinator.data.get("today")
        today_feriados = self.coordinator.data.get("today_feriados", [])
        today_no_labs = self.coordinator.data.get("today_no_laborables", [])

        attrs: dict = {
            "año": today.year if today else None,
            "fecha": today.isoformat() if today else None,
            "es_feriado": bool(today_feriados),
            "es_dia_no_laborable": bool(today_no_labs),
            "incluye_dias_judios": self.coordinator.include_jewish,
            "incluye_dias_islamicos": self.coordinator.include_islamic,
        }

        if today_feriados:
            attrs["feriados"] = [{"nombre": h["name"], "tipo": h["type"]} for h in today_feriados]
        if today_no_labs:
            attrs["dias_no_laborables"] = [
                {"nombre": h["name"], "categoria": h["category"]} for h in today_no_labs
            ]

        return attrs


def _unique(lst: list[str]) -> list[str]:
    seen: set = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
