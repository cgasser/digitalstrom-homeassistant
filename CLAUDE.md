# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Home Assistant custom integration for digitalSTROM smart home systems. It connects to a digitalSTROM server (dSS) to control and monitor digitalSTROM devices through Home Assistant.

## Architecture

The integration follows Home Assistant's standard custom component structure:

- **Entry Point**: `custom_components/digitalstrom/__init__.py` - Manages integration lifecycle, sets up platforms and event listeners
- **API Client**: `custom_components/digitalstrom/api/client.py` - Core HTTP/WebSocket client for dSS communication
- **Data Models**: `custom_components/digitalstrom/api/` - Models for apartment, zones, devices, circuits, scenes, etc.
- **Platform Components**: Individual files for each HA platform (sensor, light, switch, cover, climate, etc.)
- **Config Flow**: `config_flow.py` - Handles integration setup and authentication

### Key Components

- **DigitalstromClient**: Main API client handling authentication, HTTP requests, and WebSocket events
- **DigitalstromApartment**: High-level apartment model managing zones, devices, and circuits
- **Entity Classes**: Custom entity base classes in `entity.py` for digitalSTROM-specific functionality
- **Event System**: WebSocket-based real-time event handling with watchdog mechanism

## Development Commands

Since this is a Home Assistant custom integration, development typically involves:

1. **Testing**: Copy to Home Assistant's `custom_components/` directory and restart HA
2. **Debugging**: Enable debug logging via HA's integration page or add to `configuration.yaml`:
   ```yaml
   logger:
     logs:
       custom_components.digitalstrom: debug
       digitalstrom_api: debug
   ```
3. **Development Version**: Install latest development version via HA Developer Tools action:
   ```yaml
   action: update.install
   target:
     entity_id: update.digitalstrom_update
   data:
     version: main
   ```

## Integration Features

- **Auto-discovery**: Uses SSDP/Zeroconf for automatic dSS discovery
- **SSL Support**: Handles self-signed certificates via SHA-256 fingerprint verification
- **Real-time Events**: WebSocket connection for instant device state updates
- **Multiple Platforms**: Supports sensors, lights, switches, covers, climate, scenes, binary sensors, and events
- **Watchdog**: Automatic WebSocket reconnection mechanism

## Authentication

The integration uses a two-stage authentication:
1. **App Token**: Long-lived token obtained via username/password
2. **Session Token**: Short-lived token for API requests (auto-refreshed)

## Configuration

- **Host/Port**: dSS server connection details
- **SSL**: Certificate verification (boolean or SHA-256 fingerprint)
- **DSUID**: Unique identifier for the digitalSTROM system
- **Token**: App token for authentication

## Event Handling

The integration processes real-time events from the dSS via WebSocket:
- Device state changes
- Scene calls
- Button clicks
- System events

Events are processed through registered callbacks and translated to Home Assistant state updates.