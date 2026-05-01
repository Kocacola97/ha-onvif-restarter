import logging
import time

import voluptuous as vol
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import CONF_NOTIFY_ON_SUCCESS, DOMAIN, SERVICE_REBOOT
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
            import zeep.exceptions
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

            def _notify_failure(camera_name: str, error_summary: str) -> None:
                persistent_notification.async_create(
                    hass,
                    f"Failed to reboot camera '{camera_name}': {error_summary}",
                    title="ONVIF Restarter",
                    notification_id=f"{DOMAIN}_reboot_failed_{camera_name}",
                )
                hass.bus.async_fire(f"{DOMAIN}_event", {
                    "action": "reboot",
                    "camera": camera_name,
                    "status": "failed",
                })

            for e in targets:
                data = e.data
                host = data[CONF_HOST]
                port = data[CONF_PORT]
                camera_name = data[CONF_NAME]

                _LOGGER.info("Initiating reboot for '%s' (%s:%s)", camera_name, host, port)

                try:
                    start = time.monotonic()
                    await hass.async_add_executor_job(
                        reboot_camera,
                        host,
                        port,
                        data[CONF_USERNAME],
                        data[CONF_PASSWORD],
                        10,
                    )
                    elapsed = time.monotonic() - start
                # TimeoutError before OSError — TimeoutError is a subclass of OSError
                except TimeoutError:
                    _LOGGER.warning("Reboot timed out for '%s' — the camera may be rebooting", camera_name)
                    persistent_notification.async_create(
                        hass,
                        f"Reboot command sent to '{camera_name}' but timed out waiting for response — the camera may be rebooting normally",
                        title="ONVIF Restarter — Reboot Status Uncertain",
                        notification_id=f"{DOMAIN}_reboot_failed_{camera_name}",
                    )
                    hass.bus.async_fire(f"{DOMAIN}_event", {
                        "action": "reboot",
                        "camera": camera_name,
                        "status": "unknown",
                    })
                except OSError:
                    _LOGGER.error("Cannot reach '%s': connection refused or host unreachable", camera_name)
                    _notify_failure(camera_name, "connection refused or host unreachable")
                except Exception as err:
                    if isinstance(err, zeep.exceptions.Fault):
                        fault_str = str(err)
                        if "NotAuthorized" in fault_str or "Sender" in fault_str:
                            error_summary = "authentication failed"
                            _LOGGER.error("Authentication failed for '%s' — check username/password", camera_name)
                        else:
                            error_summary = f"ONVIF protocol fault: {fault_str}"
                            _LOGGER.error("ONVIF protocol fault for '%s': %s", camera_name, fault_str)
                        _notify_failure(camera_name, error_summary)
                    else:
                        _LOGGER.exception("Unexpected error rebooting '%s'", camera_name)
                        _notify_failure(camera_name, str(err))
                else:
                    _LOGGER.info("Reboot of '%s' completed in %.1fs — restart unconfirmed", camera_name, elapsed)
                    hass.bus.async_fire(f"{DOMAIN}_event", {
                        "action": "reboot",
                        "camera": camera_name,
                        "status": "succeeded",
                    })
                    notify = e.options.get(CONF_NOTIFY_ON_SUCCESS, e.data.get(CONF_NOTIFY_ON_SUCCESS, False))
                    if notify:
                        persistent_notification.async_create(
                            hass,
                            f"Camera '{camera_name}' rebooted successfully in {elapsed:.1f}s",
                            title="ONVIF Restarter",
                            notification_id=f"{DOMAIN}_reboot_success_{camera_name}",
                        )

        hass.services.async_register(DOMAIN, SERVICE_REBOOT, _handle_reboot, schema=_SERVICE_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.config_entries.async_entries(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_REBOOT)

    return True
