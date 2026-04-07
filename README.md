
# Mace Water Meter

<img src="https://doover.com/wp-content/uploads/Doover-Logo-Landscape-Navy-padded-small.png" alt="App Icon" style="max-width: 300px;">

**Doover application for monitoring water flow via Mace Agriflow meters**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/getdoover/mace-water-meter)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/getdoover/mace-water-meter/blob/main/LICENSE)

[Getting Started](#getting-started) • [Configuration](#configuration) • [Developer](https://github.com/getdoover/mace-water-meter/blob/main/DEVELOPMENT.md) • [Need Help?](#need-help)

<br/>

## Overview

This application connects to Mace Agriflow water meters via Modbus to provide real-time water flow monitoring, event-based alerting, and pump shutdown control through the Doover platform.

Key capabilities:

- **Real-time flow monitoring** -- reads current flow rate (ML/day), cumulative totals, battery and solar voltages via Modbus holding registers
- **Configurable register mapping** -- register addresses for flow, total, battery, solar, velocity, and depth are all configurable to support different meter firmware versions
- **Event-based alerting** -- tracks water volume per pumping event and sends notifications when configurable thresholds are exceeded
- **Pump shutdown control** -- triggers automatic pump shutdown when an event volume target is reached
- **IEEE 754 float parsing** -- reads 32-bit floats from paired 16-bit Modbus registers
- **Maintenance tracking** -- records battery change dates, service notes, and telemetry for field teams

<br/>

## Getting Started

This Doover App can be managed via the Doover CLI and installed onto devices through the Doover platform.

### Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Modbus ID** | Device ID of the meter on the Modbus network | *required* |
| **Max Flow** | Maximum expected flow rate (ML/day), used for gauge scaling | *required* |
| **Allow Shutdown** | Enable pump shutdown when a volume target is reached | `true` |
| **Flow Register** | Modbus register for current flow | `7` |
| **Total Register** | Modbus register for cumulative total | `5` |
| **Battery Register** | Modbus register for battery voltage | `9` |
| **Solar Register** | Modbus register for solar voltage | `11` |
| **Velocity Register** | Modbus register for velocity (optional) | `null` |
| **Depth Register** | Modbus register for depth (optional) | `null` |
| **Modbus Config** | Modbus connection settings (bus type, serial/TCP parameters) | serial defaults |

<br/>

## Integrations

### Tags

| Tag | Type | Description |
|-----|------|-------------|
| **alert_triggered** | boolean | Set to `true` when pump shutdown volume target is exceeded |
| **alert_message_short** | string | Short description of the shutdown reason |
| **alert_message_long** | string | Detailed shutdown message including the volume reached |

### Channels

| Channel | Description |
|---------|-------------|
| **significantEvent** | Publishes a notification when the alert volume threshold is exceeded |

### Dependencies

- **Modbus Interface** (`doover_modbus_iface`) -- provides the Modbus RTU/TCP bridge

<br/>

### Need Help?

- Email: support@doover.com
- [Doover Documentation](https://docs.doover.com)
- [Developer Guide](https://github.com/getdoover/mace-water-meter/blob/main/DEVELOPMENT.md)

<br/>

## Version History

### v1.0.0 (Current)
- Initial release
- Real-time flow monitoring via Modbus
- Configurable register addresses
- Event-based alerting and pump shutdown control
- Maintenance and telemetry UI

<br/>

## License

This app is licensed under the [Apache License 2.0](https://github.com/getdoover/mace-water-meter/blob/main/LICENSE).
