# Z-Wave Setup Guide

This guide explains how to set up real Z-Wave integration with your MyHubLocal smart home hub.

## Prerequisites

- Z-Wave USB dongle (e.g., Aeotec Z-Stick Gen5+)
- Z-Wave devices (plugs, switches, sensors, etc.)
- Node.js installed on your system

## Setting up Z-Wave JS Server

### 1. Install Z-Wave JS Server

```bash
# Install globally via npm
npm install -g @zwave-js/server

# Or using npx (recommended)
npx @zwave-js/server --help
```

### 2. Find your Z-Wave USB dongle

```bash
# List USB devices to find your Z-Wave stick
lsusb | grep -i zwave

# Check serial devices
ls /dev/ttyUSB* /dev/ttyACM*
```

Common Z-Wave dongles appear as:
- `/dev/ttyUSB0` or `/dev/ttyUSB1`
- `/dev/ttyACM0` or `/dev/ttyACM1`

### 3. Start Z-Wave JS Server

```bash
# Basic startup (replace /dev/ttyUSB0 with your device path)
npx @zwave-js/server /dev/ttyUSB0

# With specific port and logging
npx @zwave-js/server /dev/ttyUSB0 --port 3000 --log-level debug
```

The server will:
- Start on `ws://localhost:3000` by default
- Initialize your Z-Wave network
- Interview all existing Z-Wave devices
- Make devices available for discovery

## Using with MyHubLocal

Once Z-Wave JS Server is running:

1. **Start your MyHubLocal backend**:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Discover Z-Wave devices**:
   ```bash
   curl http://localhost:8000/devices/discover
   ```

3. **The system will**:
   - Connect to Z-Wave JS Server at `ws://localhost:3000`
   - Retrieve all interviewed Z-Wave nodes
   - Filter out already registered devices
   - Return new devices in the format:
     ```json
     {
       "id": "zwave-2",
       "name": "Living Room Plug",
       "type": "zwave",
       "node_id": 2,
       "manufacturer": "Aeotec",
       "product": "Smart Switch 6"
     }
     ```

## Troubleshooting

### Server Connection Issues

If you see `Cannot connect to Z-Wave JS server`:
- Verify Z-Wave JS Server is running: `netstat -an | grep 3000`
- Check the server logs for errors
- Ensure your Z-Wave dongle is properly connected

### Device Discovery Issues

If no devices are found:
- Ensure devices are properly included in your Z-Wave network
- Check that devices have completed their interview process
- Verify devices aren't already registered in `devices_registry.json`

### Fallback Behavior

When Z-Wave JS Server is not available:
- The system gracefully falls back to mock discovery
- You'll see mock devices (for development/testing)
- No errors or crashes occur

## Adding New Z-Wave Devices

1. **Include device in Z-Wave network** (using Z-Wave JS UI or other tools)
2. **Wait for interview completion**
3. **Run discovery** in MyHubLocal
4. **Add discovered devices** via the web interface

## Security Notes

- Z-Wave networks use encrypted communication
- Keep your Z-Wave network key secure
- Regularly update Z-Wave JS Server
- Consider using a dedicated Z-Wave network for smart home devices
