# MyHarvia Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

_Integration to integrate with [myharvia_integration][myharvia_integration]._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show temperature of sauna.
`switch` | Switch heater, light and fan.
`number` | Show and set Sauna temperature.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `myharvia`.
1. Download _all_ the files from the `custom_components/myharvia/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "MyHarvia"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[myharvia_integration]: https://github.com/ccormier/myharvia-hass-integration
[commits-shield]: https://img.shields.io/github/commit-activity/y/ccormier/myharvia-hass-integration.svg?style=for-the-badge
[commits]: https://github.com/ccormier/myharvia-hass-integration/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/ccormier/myharvia-hass-integration.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Chris%20Cormier%20%40ccormier-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/ccormier/myharvia-hass-integration.svg?style=for-the-badge
[releases]: https://github.com/ccormier/myharvia-hass-integration/releases
