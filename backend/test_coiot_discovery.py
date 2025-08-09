#!/usr/bin/env python3
"""
Test script for Shelly CoIoT discovery functionality
"""
import asyncio
import logging
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/home/p12146/Projects/myhublocal/backend')

from app.core.discover import discover_shelly_coiot, discover_shelly_manual, discover_wifi_devices

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_coiot_discovery():
    """Test the CoIoT multicast discovery"""
    logger.info("=== Testing Shelly CoIoT Discovery ===")
    devices = await discover_shelly_coiot()
    
    if devices:
        logger.info(f"Found {len(devices)} devices via CoIoT:")
        for device in devices:
            logger.info(f"  - {device['name']} at {device['ip']} ({device['model']})")
    else:
        logger.info("No devices found via CoIoT")
    
    return devices

async def test_manual_discovery():
    """Test manual discovery of the known device"""
    logger.info("=== Testing Manual Discovery ===")
    device = await discover_shelly_manual("10.0.0.86")
    
    if device:
        logger.info(f"Manual discovery successful:")
        logger.info(f"  - {device['name']} at {device['ip']} ({device['model']})")
    else:
        logger.info("Manual discovery failed - no device at 10.0.0.86")
    
    return device

async def test_full_wifi_discovery():
    """Test the full WiFi discovery including CoIoT"""
    logger.info("=== Testing Full WiFi Discovery ===")
    devices = await discover_wifi_devices()
    
    if devices:
        logger.info(f"Full discovery found {len(devices)} devices:")
        for device in devices:
            logger.info(f"  - {device['name']} at {device['ip']} via {device['discovered_via']}")
    else:
        logger.info("Full discovery found no devices")
    
    return devices

async def main():
    """Run all discovery tests"""
    logger.info("Starting Shelly discovery tests...")
    
    # Test individual methods
    coiot_devices = await test_coiot_discovery()
    manual_device = await test_manual_discovery()
    wifi_devices = await test_full_wifi_discovery()
    
    # Summary
    logger.info("=== Discovery Test Summary ===")
    logger.info(f"CoIoT discovery: {len(coiot_devices)} devices")
    logger.info(f"Manual discovery: {'Success' if manual_device else 'Failed'}")
    logger.info(f"Full WiFi discovery: {len(wifi_devices)} devices")
    
    return wifi_devices

if __name__ == "__main__":
    try:
        devices = asyncio.run(main())
        print(f"\nTest completed. Found {len(devices)} total devices.")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
