#!/usr/bin/env python3
"""
Test discovery directly with the app imports
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/home/p12146/Projects/myhublocal/backend')

async def test_discovery():
    """Test discovery directly"""
    try:
        # Import the discovery functions
        from app.core.discover import discover_wifi_devices, discover_shelly_coiot, discover_shelly_subnet_scan, discover_shelly_manual
        
        print("=== Testing CoIoT Discovery ===")
        coiot_devices = await discover_shelly_coiot()
        print(f"CoIoT found {len(coiot_devices)} devices")
        for device in coiot_devices:
            print(f"  - {device['name']} at {device['ip']}")
        
        print("\n=== Testing Manual Discovery ===")
        manual_device = await discover_shelly_manual("10.0.0.86")
        if manual_device:
            print(f"Manual: {manual_device['name']} at {manual_device['ip']} ({manual_device['model']})")
        else:
            print("Manual discovery failed")
        
        print("\n=== Testing Subnet Scan ===")
        subnet_devices = await discover_shelly_subnet_scan()
        print(f"Subnet scan found {len(subnet_devices)} devices")
        for device in subnet_devices:
            print(f"  - {device['name']} at {device['ip']} via {device['discovered_via']}")
        
        print("\n=== Testing Full WiFi Discovery ===")
        wifi_devices = await discover_wifi_devices()
        print(f"Full WiFi discovery found {len(wifi_devices)} devices")
        for device in wifi_devices:
            print(f"  - {device['name']} at {device['ip']} via {device['discovered_via']}")
        
        return wifi_devices
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    devices = asyncio.run(test_discovery())
    print(f"\nTotal devices found: {len(devices)}")
