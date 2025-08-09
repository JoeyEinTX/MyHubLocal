#!/usr/bin/env python3

import asyncio
import sys
import logging
import httpx

# Add the backend directory to Python path
sys.path.insert(0, '/home/p12146/Projects/myhublocal/backend')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_shelly_device(ip_address: str):
    """Test if an IP address hosts a Shelly device."""
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Testing {ip_address}...")
            
            # Test Gen2 endpoint first
            try:
                response = await client.get(
                    f"http://{ip_address}/rpc/Switch.GetStatus?id=0", 
                    timeout=3.0
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "id" in result and result.get("id") == 0:
                        device = {
                            "id": f"shellyplus_{ip_address.replace('.', '_')}",
                            "name": "Shelly Plus Plug US",
                            "ip": ip_address,
                            "type": "wifi",
                            "model": "shellyplus-plug-us",
                            "manufacturer": "Shelly",
                            "generation": "gen2",
                            "discovered_via": "subnet_scan"
                        }
                        logger.info(f"Found Shelly Gen2 device at {ip_address}")
                        return device
            except Exception as e:
                logger.debug(f"Gen2 test failed for {ip_address}: {e}")
            
            # Test Gen1 endpoint
            try:
                response = await client.get(f"http://{ip_address}/relay/0", timeout=3.0)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "ison" in result:
                        device = {
                            "id": f"shelly_{ip_address.replace('.', '_')}",
                            "name": "Shelly Plug",
                            "ip": ip_address,
                            "type": "wifi",
                            "model": "shelly-plug",
                            "manufacturer": "Shelly",
                            "generation": "gen1",
                            "discovered_via": "subnet_scan"
                        }
                        logger.info(f"Found Shelly Gen1 device at {ip_address}")
                        return device
            except Exception as e:
                logger.debug(f"Gen1 test failed for {ip_address}: {e}")
                        
    except Exception as e:
        logger.debug(f"Error testing {ip_address}: {e}")
    
    return None

async def simple_subnet_scan():
    """Simple subnet scan focusing on the 10.0.0.x range."""
    logger.info("Starting simple subnet scan...")
    
    discovered_devices = []
    
    # Test specific IPs around the known device
    test_ips = ["10.0.0.86", "10.0.0.85", "10.0.0.87", "10.0.0.1"]
    
    logger.info(f"Testing {len(test_ips)} IP addresses")
    
    semaphore = asyncio.Semaphore(3)
    
    async def test_with_limit(ip):
        async with semaphore:
            return await test_shelly_device(ip)
    
    tasks = [test_with_limit(ip) for ip in test_ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if result and not isinstance(result, Exception):
            discovered_devices.append(result)
    
    logger.info(f"Simple scan found {len(discovered_devices)} devices")
    for device in discovered_devices:
        logger.info(f"  - {device['name']} at {device['ip']}")
    
    return discovered_devices

if __name__ == "__main__":
    asyncio.run(simple_subnet_scan())
