import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_PORT, DOMAIN
from .onvif_client import test_connection

_LOGGER = logging.getLogger(__name__)


class OnvifRestarterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            existing_names = {e.data[CONF_NAME] for e in self._async_current_entries()}
            if user_input[CONF_NAME] in existing_names:
                errors[CONF_NAME] = "name_exists"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()

                try:
                    await self.hass.async_add_executor_job(
                        test_connection,
                        user_input[CONF_HOST],
                        user_input[CONF_PORT],
                        user_input[CONF_USERNAME],
                        user_input[CONF_PASSWORD],
                    )
                except Exception as err:
                    _LOGGER.warning(
                        "Config flow test_connection failed for %s:%s: %s",
                        user_input[CONF_HOST],
                        user_input[CONF_PORT],
                        err,
                    )
                    errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }),
            errors=errors,
        )
