#!/usr/bin/env python3
"""
Debug script to test Shelly device discovery
"""
import asyncio
import httpx
import ipaddress
import netifaces
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_device(ip: str):
    """Test a single IP for Shelly device"""
    timeout = httpx.Timeout(5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Test Gen2 API first
        try:
            response = await client.get(f"http://{ip}/rpc/Shelly.GetDeviceInfo")
            if response.status_code == 200:
                device_info = response.json()
                logger.info(f"Found Gen2 Shelly at {ip}: {device_info.get('name', 'Unknown')}")
                return True
        except Exception as e:
            logger.debug(f"Gen2 test failed for {ip}: {e}")
        
        # Test Gen1 API
        try:
            response = await client.get(f"http://{ip}/settings")
            if response.status_code == 200:
                device_info = response.json()
                logger.info(f"Found Gen1 Shelly at {ip}: {device_info.get('name', 'Unknown')}")
                return True
        except Exception as e:
            logger.debug(f"Gen1 test failed for {ip}: {e}")
    
    return False

async def discover_local_networks():
    """Get local network interfaces"""
    networks = []
    interfaces = netifaces.interfaces()
    
    for interface in interfaces:
        if interface.startswith(('lo', 'docker', 'br-')):
            continue
            
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr_info in addrs[netifaces.AF_INET]:
                ip = addr_info.get('addr')
                netmask = addr_info.get('netmask')
                
                if ip and netmask and not ip.startswith('127.'):
                    try:
                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                        networks.append(network)
                        logger.info(f"Found network: {network}")
                    except Exception as e:
                        logger.warning(f"Could not parse network {ip}/{netmask}: {e}")
    
    return networks

async def test_discovery():
    """Test the discovery process"""
    logger.info("Starting discovery debug test")
    
    # Get networks
    networks = await discover_local_networks()
    
    # Test specific IP first
    logger.info("\n=== Testing specific IP 10.0.0.86 ===")
    found = await test_single_device("10.0.0.86")
    if found:
        logger.info("✅ Direct test of 10.0.0.86 successful")
    else:
        logger.error("❌ Direct test of 10.0.0.86 failed")
    
    # Test subnet scan
    logger.info("\n=== Testing subnet scan ===")
    test_ips = []
    for network in networks:
        if str(network.network_address).startswith("10.0.0"):
            # Test just a few IPs around 86
            for i in range(85, 88):
                test_ips.append(f"10.0.0.{i}")
    
    logger.info(f"Testing IPs: {test_ips}")
    
    semaphore = asyncio.Semaphore(3)
    
    async def test_ip_with_semaphore(ip):
        async with semaphore:
            logger.info(f"Testing {ip}...")
            result = await test_single_device(ip)
            if result:
                logger.info(f"✅ Found device at {ip}")
            else:
                logger.info(f"❌ No device at {ip}")
            return result
    
    tasks = [test_ip_with_semaphore(ip) for ip in test_ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    found_devices = sum(1 for r in results if r is True)
    logger.info(f"\n=== Summary ===")
    logger.info(f"Tested {len(test_ips)} IPs, found {found_devices} devices")

if __name__ == "__main__":
    asyncio.run(test_discovery())
