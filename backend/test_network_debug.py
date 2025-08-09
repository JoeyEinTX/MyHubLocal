#!/usr/bin/env python3

import asyncio
import sys
import logging

# Add the backend directory to Python path
sys.path.insert(0, '/home/p12146/Projects/myhublocal/backend')

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_direct_device():
    """Test direct connection to the known device."""
    logger.info("Testing direct connection to 10.0.0.86...")
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            # Test Gen2 endpoint
            logger.info("Testing Gen2 endpoint...")
            response = await client.get("http://10.0.0.86/rpc/Switch.GetStatus?id=0", timeout=5.0)
            logger.info(f"Gen2 response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Gen2 data: {response.json()}")
            
            # Test Gen1 endpoint
            logger.info("Testing Gen1 endpoint...")
            response = await client.get("http://10.0.0.86/relay/0", timeout=5.0)
            logger.info(f"Gen1 response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Gen1 data: {response.json()}")
                
    except Exception as e:
        logger.error(f"Direct test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_network_detection():
    """Test the network detection logic."""
    logger.info("Testing network detection...")
    
    try:
        import socket
        import ipaddress
        
        # Test socket method
        logger.info("Testing socket method...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            logger.info(f"Socket method found IP: {local_ip}")
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            logger.info(f"Network: {network}")
        
        # Test hostname method
        logger.info("Testing hostname method...")
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"Hostname method found IP: {local_ip}")
        
    except Exception as e:
        logger.error(f"Network detection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_device())
    asyncio.run(test_network_detection())
