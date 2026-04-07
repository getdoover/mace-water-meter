# Mace Water Meter -- Development Guide

## Repository Structure

```
README.md                   <-- User-facing app description
DEVELOPMENT.md              <-- This file
pyproject.toml              <-- Python project config and dependencies
Dockerfile                  <-- Production Docker image
doover_config.json          <-- Doover platform metadata (generated)

src/mace_water_meter/
  __init__.py               <-- Entry point (main function)
  application.py            <-- Core application logic and UI handlers
  app_config.py             <-- Configuration schema (Modbus ID, registers, etc.)
  app_tags.py               <-- Declarative tags (display state, pump control)
  app_ui.py                 <-- UI definition (flow gauge, event counters, maintenance)
  app_state.py              <-- State machine (sleeping / awake_init / awake_rt)
  record.py                 <-- Modbus register parser (IEEE 754 float from paired registers)

simulators/
  app_config.json           <-- Sample config for local development
  docker-compose.yml        <-- Orchestrates device agent, modbus interface, simulator, and app
  mace_sim/
    main.py                 <-- Modbus TCP server emulating a Mace Agriflow meter
    pyproject.toml           <-- Simulator dependencies
    Dockerfile              <-- Simulator Docker image

tests/
  test_imports.py           <-- Import and basic validation tests
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker and Docker Compose (for simulator and deployment)

## Getting Started

### Install dependencies

```bash
uv sync
```

### Run locally (with simulator)

```bash
cd simulators
docker compose up --build
```

This starts four services:

| Service | Description |
|---------|-------------|
| `device_agent` | Doover device agent |
| `modbus_iface` | Modbus RTU/TCP bridge |
| `mace_sim` | Mace Agriflow meter simulator (TCP on port 5020) |
| `application` | This app, reading from the simulator |

### Run tests

```bash
uv run pytest tests/
```

## Architecture

### Data Flow

```
Mace Meter  -->  Modbus (RTU/TCP)  -->  modbus_iface  -->  Application  -->  Doover Platform
                                                              |
                                                              +--> Tags (pump control)
                                                              +--> Channels (alerts)
                                                              +--> UI (dashboard)
```

### Modbus Registers

The app reads 20 holding registers (type 3) starting at address 0. Register addresses are configurable via the config schema. Each value occupies two consecutive 16-bit registers, parsed as a big-endian IEEE 754 32-bit float.

Default register mapping:

| Register | Description |
|----------|-------------|
| 5-6 | Cumulative total (ML) |
| 7-8 | Current flow (ML/day) |
| 9-10 | Battery voltage (V) |
| 11-12 | Solar voltage (V) |
| 1-2 | Velocity (m/s) -- optional |
| 3-4 | Depth (m) -- optional |

### State Machine

| State | Description | Timeout |
|-------|-------------|---------|
| `initial` | Startup, transitions immediately to `awake_init` | -- |
| `sleeping` | Low-power mode, no Modbus requests | 15 min |
| `awake_init` | Waiting for first successful reading | 15s |
| `awake_rt` | Real-time reading mode, actively polling | 2 min |

### UI

The UI uses static declarative elements with `setup()` to configure config-dependent properties (precision based on `max_flow`, flow gauge ranges, shutdown visibility).

## Regenerating doover_config.json

```bash
uv run export-config
```

## Building the Docker Image

```bash
docker build -t mace-water-meter .
```
