# ONVIF Camera Restarter

A Home Assistant custom integration that lets you reboot ONVIF-compatible cameras (tested with D-Link) via a HA service — schedulable through automations.

## Features

- Add any number of cameras with static IPs and credentials
- Reboot a single camera by name or all cameras at once
- Schedule reboots via HA automations (e.g. nightly at 3am)
- Trigger manual reboots from Developer Tools → Services

## Installation

### Via HACS (recommended)

1. In HA, open **HACS → Integrations**
2. Click the three-dot menu → **Custom repositories**
3. Add this repository URL, category: **Integration**
4. Find **ONVIF Camera Restarter** and install it
5. Restart Home Assistant

### Manual

Copy the `custom_components/onvif_restarter/` folder into your HA `config/custom_components/` directory and restart.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **ONVIF Camera Restarter**
3. Fill in the camera details:
   - **Camera name** — a unique display name (e.g. `Garage`)
   - **IP address** — the camera's static IP
   - **ONVIF port** — default is `80`
   - **Username / Password** — ONVIF credentials
4. Repeat for each camera

## Usage

### Reboot a single camera

Call the service `onvif_restarter.reboot_camera` with:

```yaml
service: onvif_restarter.reboot_camera
data:
  name: Garage
```

### Reboot all cameras

```yaml
service: onvif_restarter.reboot_camera
data:
  all: true
```

### Schedule via automation

```yaml
automation:
  alias: Nightly camera reboot
  trigger:
    - platform: time
      at: "03:00:00"
  action:
    - service: onvif_restarter.reboot_camera
      data:
        all: true
```

## Requirements

- Home Assistant 2024.1 or newer
- Cameras must support the ONVIF Device Management Service (`SystemReboot` command)
- Cameras must have static IPs on your local network

## License

MIT
