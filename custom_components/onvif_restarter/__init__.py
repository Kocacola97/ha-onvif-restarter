import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SERVICE_REBOOT
from .onvif_client import reboot_camera

_LOGGER = logging.getLogger(__name__)

_SERVICE_SCHEMA = vol.Schema({
    vol.Optional("name"): cv.string,
    vol.Optional("all"): cv.boolean,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    if not hass.services.has_service(DOMAIN, SERVICE_REBOOT):
        async def _handle_reboot(call: ServiceCall) -> None:
            name = call.data.get("name")
            reboot_all = call.data.get("all", False)

            if not reboot_all and not name:
                _LOGGER.error("reboot_camera requires 'name' or 'all: true'")
                return

            entries = hass.config_entries.async_entries(DOMAIN)
            targets = entries if reboot_all else [e for e in entries if e.data[CONF_NAME] == name]

            if not targets:
                _LOGGER.error("No camera named '%s' configured", name)
                return

            for e in targets:
                data = e.data
                try:
                    await hass.async_add_executor_job(
                        reboot_camera,
                        data[CONF_HOST],
                        data[CONF_PORT],
                        data[CONF_USERNAME],
                        data[CONF_PASSWORD],
                    )
                    _LOGGER.info("Reboot sent to '%s' (%s:%s)", data[CONF_NAME], data[CONF_HOST], data[CONF_PORT])
                except Exception as err:
                    _LOGGER.error("Failed to reboot '%s': %s", data[CONF_NAME], err)

        hass.services.async_register(DOMAIN, SERVICE_REBOOT, _handle_reboot, schema=_SERVICE_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.config_entries.async_entries(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_REBOOT)

    return True
