"""Config flow for Feriados Argentina."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class FeriadosArgentinaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow - only one instance allowed."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Only allow a single instance of this integration
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Holiday Days Argentina", data={})

        return self.async_show_form(step_id="user")
