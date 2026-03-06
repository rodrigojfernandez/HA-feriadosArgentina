"""Config flow for Feriados Argentina."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_INCLUDE_ISLAMIC, CONF_INCLUDE_JEWISH, DOMAIN

_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_INCLUDE_JEWISH, default=False): bool,
        vol.Required(CONF_INCLUDE_ISLAMIC, default=False): bool,
    }
)


class FeriadosArgentinaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow — only one instance allowed."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Only allow a single instance of this integration
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Holiday Days Argentina", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_SCHEMA,
            description_placeholders={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FeriadosArgentinaOptionsFlow()


class FeriadosArgentinaOptionsFlow(config_entries.OptionsFlow):
    """Options flow to change Jewish/Islamic preferences after setup."""

    async def async_step_init(self, user_input=None):
        current = self.config_entry.options or self.config_entry.data

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_INCLUDE_JEWISH,
                    default=current.get(CONF_INCLUDE_JEWISH, False),
                ): bool,
                vol.Required(
                    CONF_INCLUDE_ISLAMIC,
                    default=current.get(CONF_INCLUDE_ISLAMIC, False),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
