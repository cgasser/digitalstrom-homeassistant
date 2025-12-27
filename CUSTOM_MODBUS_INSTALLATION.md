# Custom Modbus Meter Support - Manual Installation Guide

This fork contains custom modifications to add Modbus meter support via the digitalSTROM REST API. If you install the integration via HACS (which pulls from the upstream repository), you'll need to manually apply these custom changes to enable Modbus meter functionality.

## Overview

The custom changes add support for reading Modbus meter data through the digitalSTROM REST API (`/api/v1/apartment/meterings/values`) instead of the standard JSON API. This enables monitoring of external energy meters connected via Modbus to your digitalSTROM server.

## Custom Commits

This fork includes two custom commits:
- `107ea4d` - Add initial modbus meter support via REST API
- `7ace92d` - Enhance modbus meter device information and separation

## Files Modified

The following files contain custom modifications that differ from the upstream repository:

### 1. `custom_components/digitalstrom/api/client.py`

**What changed**: Added `_request_rest_api()` method and modified `request()` to use REST API for metering endpoints.

**Location**: Lines 145-176 and lines 183-190

**Key additions**:
```python
async def _request_rest_api(self, url: str) -> dict:
    # Make a request to the REST API (v1) instead of JSON API
    if (self.last_request is None) or (
        self.last_request < time.time() - SESSION_TOKEN_TIMEOUT
    ):
        self._session_token = await self.request_session_token()

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=self.ssl),
        cookies=dict(token=self._session_token),
        loop=self._loop,
    ) as session:
        try:
            async with session.get(
                url=f"https://{self.host}:{self.port}/api/v1/{url}"
            ) as response:
                # ... error handling ...
                return data
```

And in the `request()` method:
```python
# Use REST API for meterings endpoints
if "apartment/meterings" in url:
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Using REST API for: %s", url)
    data = await self._request_rest_api(url)
    return data
```

### 2. `custom_components/digitalstrom/api/channel.py`

**What changed**: Added `DigitalstromModbusMeterChannel` class.

**Location**: Lines 115-152

**Key addition**:
```python
class DigitalstromModbusMeterChannel(DigitalstromChannel):
    def __init__(self, apartment, meter_id: str, meter_type: str, meter_name: str = None, device_info: dict = None):
        super().__init__(apartment, meter_id)
        self.meter_type = meter_type
        self.meter_id = meter_id
        self.meter_name = meter_name or f"Meter {meter_id}"
        self.apartment = apartment
        self.device_info = device_info or {}

    async def get_value(self) -> float:
        try:
            values_data = await self.apartment.client.request("apartment/meterings/values")
            if data := values_data.get("data"):
                if values := data.get("values"):
                    for value_entry in values:
                        if value_entry.get("id") == self.meter_id:
                            attributes = value_entry.get("attributes", {})
                            value = attributes.get("value", 0.0)

                            if self.meter_type == "power":
                                return float(value)
                            elif self.meter_type == "energy_consumed":
                                return float(value)
                            # ... additional meter types ...
```

### 3. `custom_components/digitalstrom/api/meter.py`

**What changed**: This is an entirely new file.

**Purpose**: Defines the `DigitalstromMeter` class for meter device metadata.

**Full file content**: 36 lines defining meter properties (name, manufacturer, model, serial, power, energy).

### 4. `custom_components/digitalstrom/sensor.py`

**What changed**: Added `DigitalstromModbusMeterSensor` class and setup logic.

**Location**: Lines 61-100 (setup logic) and lines 521-581 (sensor class)

**Key additions in `async_setup_entry()`**:
```python
# Get modbus meter data from REST API
try:
    meterings_data = await client.request("apartment/meterings/values")

    # Parse the nested structure: {'data': {'values': [...]}}
    if (data := meterings_data.get("data")) and (values := data.get("values")):
        # Group values by serial number and slave address
        meter_groups = {}
        for value_entry in values:
            meter_id = value_entry.get("id")
            # ... grouping logic ...

        # Create sensor entities for each meter
        for group_key, meter_values in meter_groups.items():
            # ... create sensors for power and energy ...
```

**New sensor class**:
```python
class DigitalstromModbusMeterSensor(SensorEntity):
    def __init__(self, channel: DigitalstromModbusMeterChannel):
        self.channel = channel
        self._attr_unique_id = f"modbus_{channel.meter_id}_{channel.meter_type}"
        # ... device info creation ...

    async def async_update(self):
        value = await self.channel.get_value()
        if value is not None:
            self._attr_native_value = value
```

## Manual Installation Steps

After installing the integration via HACS, follow these steps to enable Modbus meter support:

### Step 1: Backup the HACS Installation

```bash
cd /config/custom_components/digitalstrom
cp -r . ../digitalstrom.backup
```

### Step 2: Download Custom Files

Download the following files from this fork repository (https://github.com/cgasser/digitalstrom-homeassistant):

1. `custom_components/digitalstrom/api/client.py`
2. `custom_components/digitalstrom/api/channel.py`
3. `custom_components/digitalstrom/api/meter.py`
4. `custom_components/digitalstrom/sensor.py`

### Step 3: Replace Files

Copy the downloaded files to your Home Assistant installation, replacing the HACS versions:

```bash
# Replace client.py
cp /path/to/downloaded/client.py /config/custom_components/digitalstrom/api/client.py

# Replace channel.py
cp /path/to/downloaded/channel.py /config/custom_components/digitalstrom/api/channel.py

# Add new meter.py (if it doesn't exist)
cp /path/to/downloaded/meter.py /config/custom_components/digitalstrom/api/meter.py

# Replace sensor.py
cp /path/to/downloaded/sensor.py /config/custom_components/digitalstrom/sensor.py
```

### Step 4: Restart Home Assistant

After replacing the files, restart Home Assistant for the changes to take effect.

### Step 5: Verify Modbus Meters

After restart, check the Developer Tools > States page for new entities with IDs like:
- `sensor.modbus_<serial>_<slave>_power`
- `sensor.modbus_<serial>_<slave>_energy_consumed`

## What Features Are Added

With these custom modifications, you gain:

1. **Automatic Modbus Meter Discovery**: All Modbus meters connected to your digitalSTROM server are automatically detected and added as sensors.

2. **Power Monitoring**: Real-time power consumption/production in watts.

3. **Energy Monitoring**: Cumulative energy consumption/production in Wh (watt-hours).

4. **Device Separation**: Meters are properly separated by serial number and Modbus slave address.

5. **Proper Device Info**: Each meter appears as a separate device in Home Assistant with:
   - Manufacturer: "Modbus Meter"
   - Model: Based on serial number and slave address
   - Identifiers: Unique per meter

## Technical Details

### REST API vs JSON API

The upstream integration uses the digitalSTROM JSON API for most operations. However, Modbus meter data is only available through the REST API v1 endpoint:

- **REST API endpoint**: `https://<dss>:<port>/api/v1/apartment/meterings/values`
- **Returns**: Nested JSON structure with meter readings

### Data Structure

The REST API returns data in this format:
```json
{
  "data": {
    "values": [
      {
        "id": "meter_id",
        "type": "type",
        "attributes": {
          "value": 123.45,
          "serial": "12345678",
          "slaveAddress": 1,
          "register": "power"
        }
      }
    ]
  }
}
```

## Maintaining Compatibility

When the upstream repository receives updates:

1. **Check for conflicts**: Compare the upstream changes against the custom files listed above.

2. **Manual merge**: If upstream modifies any of the custom files, you'll need to manually merge:
   - Keep the custom Modbus functionality
   - Integrate upstream bug fixes and improvements
   - Test thoroughly after merging

3. **Update this guide**: If significant changes occur, update this documentation.

## Support

For issues related to:
- **Upstream integration**: Report to https://github.com/Mat931/digitalstrom-homeassistant/issues
- **Modbus meter functionality**: Report to https://github.com/cgasser/digitalstrom-homeassistant/issues

## Version Information

- **Fork repository**: https://github.com/cgasser/digitalstrom-homeassistant
- **Upstream repository**: https://github.com/Mat931/digitalstrom-homeassistant
- **Last synchronized**: Commit `7ace92d` (includes upstream version 0.0.13)

## Future Considerations

These custom changes could potentially be contributed back to the upstream repository if:
1. Other users need Modbus meter support
2. The implementation is generalized and tested across different setups
3. The upstream maintainer accepts the feature

Until then, this manual installation process preserves the functionality while allowing you to benefit from upstream updates.
