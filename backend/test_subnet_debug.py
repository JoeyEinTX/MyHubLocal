#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/home/p12146/Projects/myhublocal/backend')

async def test_subnet_scan():
    print("Starting subnet scan test...")
    
    try:
        # Try to import
        print("Importing discover module...")
        from app.core.discover import discover_shelly_subnet_scan
        print("Import successful")
        
        # Try to run with a timeout
        print("Running subnet scan with 10 second timeout...")
        devices = await asyncio.wait_for(discover_shelly_subnet_scan(), timeout=10.0)
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device}")
            
    except asyncio.TimeoutError:
        print("Subnet scan timed out after 10 seconds")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subnet_scan())
