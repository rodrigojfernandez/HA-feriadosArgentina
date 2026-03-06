"""Data coordinator for Feriados Argentina."""

from __future__ import annotations

import logging
import re
from datetime import date, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URL,
    DIA_NO_LABORABLE_TYPE,
    DOMAIN,
    FERIADO_TYPES,
    ISLAMIC_MARKER,
    JEWISH_MARKER,
)

_LOGGER = logging.getLogger(__name__)

# Check for updates every 12 hours; actual re-fetch only happens on the 1st of each month
SCAN_INTERVAL = timedelta(hours=12)


def _classify_holiday(name: str, holiday_type: str) -> str:
    """Return 'feriado', 'no_laborable_judio', 'no_laborable_islamico', or 'no_laborable'."""
    if holiday_type in FERIADO_TYPES:
        return "feriado"
    if holiday_type == DIA_NO_LABORABLE_TYPE:
        if JEWISH_MARKER in name:
            return "no_laborable_judio"
        if ISLAMIC_MARKER in name:
            return "no_laborable_islamico"
        return "no_laborable"
    return "no_laborable"


def _parse_holidays(html: str) -> dict[tuple[int, int], list[dict]]:
    """Parse all holidays from the HTML of the argentina.gob.ar page."""
    holidays: dict[tuple[int, int], list[dict]] = {}

    for month_match in re.finditer(r'id="feriados-(\d+)">(.*?)</ul>', html, re.DOTALL):
        month = int(month_match.group(1))
        ul_content = month_match.group(2)

        for li_match in re.finditer(r"<li>(.*?)</li>", ul_content, re.DOTALL):
            li = li_match.group(1)

            # Extract referenced day numbers from id="feriado-DAY-MONTH"
            days = [int(d) for d in re.findall(r'id="feriado-(\d+)-\d+"', li)]
            if not days:
                continue

            # Extract holiday type from the sr-only span
            type_match = re.search(r'class="sr-only">(.*?)</span>', li)
            holiday_type = ""
            if type_match:
                holiday_type = (
                    type_match.group(1)
                    .replace("&nbsp;", " ")
                    .replace("\xa0", " ")
                    .strip()
                    .strip("—")
                    .strip()
                )

            # Extract holiday name: text after the last </span>
            name_match = re.search(r"</span>\s*([^<]+?)\s*$", li.strip())
            name = name_match.group(1).strip().rstrip(".") if name_match else ""

            category = _classify_holiday(name, holiday_type)

            for day in days:
                key = (month, day)
                if key not in holidays:
                    holidays[key] = []
                holidays[key].append(
                    {
                        "name": name,
                        "type": holiday_type,
                        "category": category,
                    }
                )

    return holidays


class ArgentinaHolidaysCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches Argentine holidays once per month."""

    def __init__(self, hass: HomeAssistant, include_jewish: bool, include_islamic: bool) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.include_jewish = include_jewish
        self.include_islamic = include_islamic
        self._holidays: dict = {}
        self._fetched_year: int = 0
        self._fetched_month: int = 0

    async def _async_update_data(self) -> dict:
        """Fetch holidays if it's the first day of a new month or data is stale."""
        today = date.today()
        year = today.year
        month = today.month

        needs_fetch = (
            not self._holidays
            or self._fetched_year != year
            or (today.day == 1 and self._fetched_month != month)
        )

        if needs_fetch:
            url = BASE_URL.format(year=year)
            _LOGGER.info("Fetching holidays for %d from %s", year, url)
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp,
                ):
                    if resp.status != 200:
                        raise UpdateFailed(f"HTTP {resp.status} while fetching holidays from {url}")
                    html = await resp.text()
            except aiohttp.ClientError as err:
                raise UpdateFailed(f"Network error while fetching holidays: {err}") from err

            self._holidays = _parse_holidays(html)
            self._fetched_year = year
            self._fetched_month = month
            _LOGGER.debug(
                "Loaded %d days with holidays/non-working days for %d",
                len(self._holidays),
                year,
            )

        today_key = (today.month, today.day)
        all_today = self._holidays.get(today_key, [])

        # Filter according to user preferences
        def _is_visible(entry: dict) -> bool:
            cat = entry["category"]
            if cat == "feriado":
                return True
            if cat == "no_laborable_judio":
                return self.include_jewish
            if cat == "no_laborable_islamico":
                return self.include_islamic
            # generic no_laborable (e.g. Armenian, tolerance day) — always include
            return True

        today_visible = [e for e in all_today if _is_visible(e)]

        return {
            "holidays": self._holidays,
            "today": today,
            "today_all": all_today,
            "today_holidays": today_visible,
            "today_feriados": [e for e in today_visible if e["category"] == "feriado"],
            "today_no_laborables": [e for e in today_visible if e["category"] != "feriado"],
        }
