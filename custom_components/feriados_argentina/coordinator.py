"""Data coordinator for Feriados Argentina."""

from __future__ import annotations

import logging
from datetime import date, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, DOMAIN, HOLIDAY_API_TYPES, NON_WORKING_DAY_API_TYPES

_LOGGER = logging.getLogger(__name__)

# Check for updates every 12 hours
SCAN_INTERVAL = timedelta(hours=12)


def _parse_holidays_from_api(data: list[dict]) -> dict[tuple[int, int], list[dict]]:
    """Parse holidays from ArgentinaDatos API response.

    Args:
        data: List of holiday dictionaries from the API

    Returns:
        Dictionary mapping (month, day) tuples to lists of holiday entries
    """
    holidays: dict[tuple[int, int], list[dict]] = {}

    for item in data:
        date_str = item.get("fecha", "")
        name = item.get("nombre", "")
        api_type = item.get("tipo", "")

        # Parse date (format: YYYY-MM-DD)
        try:
            year, month, day = date_str.split("-")
            month = int(month)
            day = int(day)
        except ValueError:
            _LOGGER.warning("Could not parse date: %s", date_str)
            continue

        # Map API type to English type and category
        type_map = {
            "inamovible": "Fixed holiday",
            "trasladable": "Movable holiday",
            "puente": "Bridge day",
        }
        holiday_type = type_map.get(api_type, api_type)

        # Classify: holiday vs non-working day
        if api_type in HOLIDAY_API_TYPES:
            category = "holiday"
        elif api_type in NON_WORKING_DAY_API_TYPES:
            category = "non_working_day"
        else:
            category = "holiday"

        key = (month, day)
        if key not in holidays:
            holidays[key] = []

        entry = {
            "name": name,
            "type": holiday_type,
            "category": category,
        }
        if entry not in holidays[key]:
            holidays[key].append(entry)

    return holidays


class ArgentinaHolidaysCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches Argentine holidays from ArgentinaDatos API."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._holidays: dict = {}
        self._fetched_year: int = 0

    async def _async_update_data(self) -> dict:
        """Fetch holidays from the API if needed.

        Returns:
            Dictionary with holiday data for today
        """
        today = date.today()
        year = today.year

        # Fetch if we don't have data or year changed
        needs_fetch = not self._holidays or self._fetched_year != year

        if needs_fetch:
            url = API_URL.format(year=year)
            _LOGGER.info("Fetching holidays for %d from %s", year, url)
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp,
                ):
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status} while fetching holidays from {url}")
                    data = await resp.json()
            except aiohttp.ClientError as err:
                raise UpdateFailed(f"Network error while fetching holidays: {err}") from err

            self._holidays = _parse_holidays_from_api(data)
            self._fetched_year = year
            _LOGGER.debug(
                "Loaded %d holiday dates for %d",
                len(self._holidays),
                year,
            )

        today_key = (today.month, today.day)
        all_today = self._holidays.get(today_key, [])

        # Separate holidays from non-working days
        today_holidays = [e for e in all_today if e["category"] == "holiday"]
        today_non_working = [e for e in all_today if e["category"] == "non_working_day"]

        return {
            "holidays": self._holidays,
            "today": today,
            "today_all": all_today,
            "today_holidays": today_holidays,
            "today_non_working_days": today_non_working,
        }
