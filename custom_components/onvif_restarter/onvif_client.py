import logging
import os

_LOGGER = logging.getLogger(__name__)


def reboot_camera(host: str, port: int, username: str, password: str, timeout: int = 10) -> None:
    import onvif
    from onvif import ONVIFCamera

    wsdl_dir = os.path.join(os.path.dirname(onvif.__file__), "wsdl")

    _LOGGER.debug("Connecting to camera %s:%s", host, port)
    cam = ONVIFCamera(host, port, username, password, wsdl_dir, timeout=timeout)
    _LOGGER.debug("Creating devicemgmt service for %s:%s", host, port)
    devicemgmt = cam.create_devicemgmt_service()
    _LOGGER.debug("Sending SystemReboot to %s:%s", host, port)
    devicemgmt.SystemReboot()


def test_connection(host: str, port: int, username: str, password: str, timeout: int = 10) -> None:
    import onvif
    from onvif import ONVIFCamera

    wsdl_dir = os.path.join(os.path.dirname(onvif.__file__), "wsdl")

    _LOGGER.debug("test_connection: connecting to %s:%s", host, port)
    cam = ONVIFCamera(host, port, username, password, wsdl_dir, timeout=timeout)

    _LOGGER.debug("test_connection: creating devicemgmt service for %s:%s", host, port)
    devicemgmt = cam.create_devicemgmt_service()

    _LOGGER.debug("test_connection: calling GetSystemDateAndTime on %s:%s", host, port)
    devicemgmt.GetSystemDateAndTime()
