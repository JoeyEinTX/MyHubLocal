#!/usr/bin/env python3
"""
Quick test of discovery functions
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

async def test_manual_discovery():
    """Test manual discovery of known device"""
    from app.core.discover import discover_shelly_manual
    
    print("=== Testing Manual Discovery ===")
    print("Testing known device at 10.0.0.86...")
    
    try:
        device = await discover_shelly_manual("10.0.0.86")
        if device:
            print(f"✅ Found device: {device['name']} ({device['model']})")
            print(f"   IP: {device['ip']}")
            print(f"   Generation: {device['generation']}")
            print(f"   Discovery method: {device['discovered_via']}")
        else:
            print("❌ No device found at 10.0.0.86")
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_subnet_scan():
    """Test subnet scanning with limited range"""
    from app.core.discover import discover_shelly_subnet_scan
    
    print("\n=== Testing Subnet Scan ===")
    print("Scanning for Shelly devices...")
    
    try:
        devices = await discover_shelly_subnet_scan()
        print(f"Found {len(devices)} devices via subnet scan:")
        for device in devices:
            print(f"  - {device['name']} at {device['ip']} ({device['model']})")
    except Exception as e:
        print(f"❌ Subnet scan error: {e}")

async def main():
    print("Testing discovery functions...\n")
    
    # Test manual discovery first (fastest)
    await test_manual_discovery()
    
    # Test subnet scan (slower but should find the device)
    await test_subnet_scan()
    
    print("\n=== Test complete ===")

if __name__ == "__main__":
    asyncio.run(main())
