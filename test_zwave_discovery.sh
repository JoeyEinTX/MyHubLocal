#!/bin/bash
# Test script to demonstrate Z-Wave discovery functionality

echo "🏠 MyHubLocal Z-Wave Discovery Test"
echo "======================================"
echo

# Check if Z-Wave JS Server is running
echo "🔍 Checking for Z-Wave JS Server..."
if nc -z localhost 3000 2>/dev/null; then
    echo "✅ Z-Wave JS Server detected at localhost:3000"
    echo "   Real Z-Wave discovery will be used"
else
    echo "⚠️  Z-Wave JS Server not detected at localhost:3000"
    echo "   Falling back to mock discovery for development"
    echo
    echo "💡 To set up real Z-Wave integration:"
    echo "   1. Connect your Z-Wave USB dongle"
    echo "   2. Install: npm install -g @zwave-js/server"
    echo "   3. Run: npx @zwave-js/server /dev/ttyUSB0"
    echo "   4. See docs/ZWAVE_SETUP.md for detailed instructions"
fi

echo
echo "🔍 Testing device discovery..."

# Test the discovery endpoint
response=$(curl -s http://localhost:8000/devices/discover)

if [ $? -eq 0 ]; then
    echo "✅ Discovery endpoint responded successfully"
    
    # Parse the response to show discovered devices
    echo
    echo "📱 Discovered devices:"
    echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
devices = data.get('discovered_devices', [])
summary = data.get('discovery_summary', {})

print(f'   Total: {summary.get(\"total_discovered\", 0)} devices')
print(f'   Wi-Fi: {summary.get(\"wifi_devices\", 0)} devices')
print(f'   Z-Wave: {summary.get(\"zwave_devices\", 0)} devices')
print()

for device in devices:
    discovered_via = device.get('discovered_via', 'unknown')
    if device.get('type') == 'zwave':
        print(f'   📡 {device.get(\"name\", \"Unknown\")} (Node {device.get(\"node_id\", \"?\")})')
        print(f'      ID: {device.get(\"id\", \"unknown\")}')
        print(f'      Discovery: {discovered_via}')
        if discovered_via == 'mock':
            print(f'      ⚠️  This is a mock device for testing')
        print()
    else:
        print(f'   📶 {device.get(\"name\", \"Unknown\")} ({device.get(\"ip\", \"no IP\")})')
        print(f'      ID: {device.get(\"id\", \"unknown\")}')
        print(f'      Discovery: {discovered_via}')
        print()
"
else
    echo "❌ Failed to connect to discovery endpoint"
    echo "   Make sure the backend server is running:"
    echo "   cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
fi

echo
echo "🎯 Next steps:"
echo "   • Add discovered devices via the web interface"
echo "   • Control devices via /devices/{id}/state endpoint"
echo "   • Monitor device status via /devices/status/{id}"
