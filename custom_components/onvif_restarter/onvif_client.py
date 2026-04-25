import logging
import os

_LOGGER = logging.getLogger(__name__)


def reboot_camera(host: str, port: int, username: str, password: str) -> None:
    import onvif
    from onvif import ONVIFCamera

    wsdl_dir = os.path.join(os.path.dirname(onvif.__file__), "wsdl")
    cam = ONVIFCamera(host, port, username, password, wsdl_dir)
    devicemgmt = cam.create_devicemgmt_service()
    devicemgmt.SystemReboot()
    _LOGGER.debug("Reboot command sent to %s:%s", host, port)


def test_connection(host: str, port: int, username: str, password: str) -> None:
    import onvif
    from onvif import ONVIFCamera

    wsdl_dir = os.path.join(os.path.dirname(onvif.__file__), "wsdl")
    cam = ONVIFCamera(host, port, username, password, wsdl_dir)
    devicemgmt = cam.create_devicemgmt_service()
    devicemgmt.GetSystemDateAndTime()
