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
    coordinator: ArgentinaHolidaysCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            EsFeriadoBinarySensor(coordinator),
            EsDiaNoLaborableBinarySensor(coordinator),
        ]
    )


class _BaseArgentinaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class with shared device info."""

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


class EsFeriadoBinarySensor(_BaseArgentinaBinarySensor):
    """True when today is an official national holiday (feriado)."""

    _attr_name = "Es feriado hoy"
    _attr_unique_id = "feriados_argentina_es_feriado"
    _attr_icon = "mdi:calendar-star"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("today_feriados"))

    @property
    def extra_state_attributes(self) -> dict:
        feriados = self.coordinator.data.get("today_feriados", [])
        today = self.coordinator.data.get("today")
        attrs: dict = {
            "año": today.year if today else None,
            "fecha": today.isoformat() if today else None,
        }
        if feriados:
            attrs["nombre"] = ", ".join(
                _unique([h["name"] for h in feriados])
            )
            attrs["tipo"] = ", ".join(
                _unique([h["type"] for h in feriados])
            )
            attrs["feriados"] = feriados
        return attrs


class EsDiaNoLaborableBinarySensor(_BaseArgentinaBinarySensor):
    """True when today is a non-working day (día no laborable) per user's config."""

    _attr_name = "Es día no laborable hoy"
    _attr_unique_id = "feriados_argentina_es_no_laborable"
    _attr_icon = "mdi:calendar-remove"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("today_no_laborables"))

    @property
    def extra_state_attributes(self) -> dict:
        no_labs = self.coordinator.data.get("today_no_laborables", [])
        today = self.coordinator.data.get("today")
        attrs: dict = {
            "año": today.year if today else None,
            "fecha": today.isoformat() if today else None,
            "incluye_dias_judios": self.coordinator.include_jewish,
            "incluye_dias_islamicos": self.coordinator.include_islamic,
        }
        if no_labs:
            attrs["nombre"] = ", ".join(
                _unique([h["name"] for h in no_labs])
            )
            attrs["categoria"] = ", ".join(
                _unique([h["category"] for h in no_labs])
            )
            attrs["dias_no_laborables"] = no_labs
        return attrs


def _unique(lst: list[str]) -> list[str]:
    seen: set = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
