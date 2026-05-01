from homeassistant.core import HomeAssistant, Event, callback

DOMAIN = "onvif_restarter"


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event,
) -> None:
    @callback
    def _describe(event: Event) -> dict:
        data = event.data
        camera = data.get("camera", "unknown")
        status = data.get("status")

        if status == "succeeded":
            message = "rebooted successfully"
        elif status == "unknown":
            message = "reboot command sent — status uncertain (camera may be rebooting)"
        else:
            message = "reboot failed"

        return {"name": camera, "message": message}

    async_describe_event(DOMAIN, f"{DOMAIN}_event", _describe)
