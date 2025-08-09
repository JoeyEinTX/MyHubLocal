"""
Device discovery module for Wi-Fi, Z-Wave, and Govee devices.
Provides async functions to scan for Shelly plugs, Z-Wave devices, and Govee LEDs.
"""
import asyncio
import logging
import socket
import ipaddress
import struct
import time
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Discovery timeouts in seconds
WIFI_DISCOVERY_TIMEOUT = 8  # Reduced timeout for better UI responsiveness
ZWAVE_DISCOVERY_TIMEOUT = 5
GOVEE_DISCOVERY_TIMEOUT = 5

# Shelly CoAP/CoIoT discovery constants
SHELLY_COAP_MULTICAST_GROUP = "224.0.1.187"
SHELLY_COAP_PORT = 5683
SHELLY_COIOT_DISCOVERY_TIMEOUT = 3  # Seconds to listen for CoIoT broadcasts

async def discover_shelly_coiot() -> List[Dict[str, Any]]:
    """
    Discover Shelly devices using their native CoAP (CoIoT) multicast protocol.
    
    Shelly devices broadcast status messages to multicast group 224.0.1.187:5683
    when CoIoT is enabled. This function listens for these broadcasts and extracts
    device information including IP address, MAC, model, and firmware version.
    
    Returns:
        List of discovered Shelly devices with detailed information from CoIoT packets.
    """
    discovered_devices = []
    
    try:
        logger.info(f"Starting Shelly CoIoT discovery (listening for {SHELLY_COIOT_DISCOVERY_TIMEOUT}s)...")
        
        # Create UDP socket for multicast reception
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Enable receiving multicast packets
        try:
            # Bind to the multicast group and port
            sock.bind(('', SHELLY_COAP_PORT))
            
            # Join the multicast group
            # struct.pack formats: '4sl' = 4-byte IP address + 4-byte interface (INADDR_ANY)
            mreq = struct.pack('4sl', socket.inet_aton(SHELLY_COAP_MULTICAST_GROUP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            # Set socket to non-blocking for async operation
            sock.setblocking(False)
            
            logger.debug(f"Listening for Shelly CoIoT broadcasts on {SHELLY_COAP_MULTICAST_GROUP}:{SHELLY_COAP_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to set up multicast socket: {e}")
            sock.close()
            return []
        
        # Track discovered devices by IP to avoid duplicates
        discovered_by_ip = {}
        start_time = time.time()
        
        # Listen for CoIoT packets with timeout
        while time.time() - start_time < SHELLY_COIOT_DISCOVERY_TIMEOUT:
            try:
                # Use asyncio to make socket operations non-blocking
                loop = asyncio.get_event_loop()
                
                # Wait for data with a short timeout to allow periodic checking
                try:
                    data, addr = await asyncio.wait_for(
                        loop.sock_recvfrom(sock, 1024), 
                        timeout=0.1
                    )
                    
                    # Parse the CoIoT packet and extract device info
                    device_info = _parse_shelly_coiot_packet(data, addr[0])
                    
                    if device_info and device_info['ip'] not in discovered_by_ip:
                        discovered_by_ip[device_info['ip']] = device_info
                        discovered_devices.append(device_info)
                        logger.info(f"Discovered Shelly device via CoIoT: {device_info['name']} at {device_info['ip']}")
                        
                except asyncio.TimeoutError:
                    # No data received in this iteration, continue listening
                    continue
                except Exception as e:
                    logger.debug(f"Error receiving CoIoT packet: {e}")
                    continue
                    
            except Exception as e:
                logger.debug(f"Error in CoIoT discovery loop: {e}")
                break
        
        # Clean up socket
        try:
            # Leave the multicast group
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            sock.close()
        except:
            pass
        
        logger.info(f"CoIoT discovery completed. Found {len(discovered_devices)} devices.")
        
    except Exception as e:
        logger.error(f"Shelly CoIoT discovery failed: {e}")
    
    return discovered_devices

def _parse_shelly_coiot_packet(data: bytes, source_ip: str) -> Optional[Dict[str, Any]]:
    """
    Parse a Shelly CoIoT (CoAP) packet to extract device information.
    
    Shelly CoIoT packets contain JSON-like data with device status and metadata.
    This function attempts to extract useful information like device model,
    MAC address, firmware version, and current status.
    
    Args:
        data: Raw packet data received from multicast
        source_ip: IP address of the device that sent the packet
    
    Returns:
        Dictionary with device information, or None if packet is not from a Shelly device
    """
    try:
        # CoAP packets have a specific structure, but Shelly devices often send
        # JSON payloads in the packet data. We'll look for recognizable patterns.
        
        # Convert bytes to string, handling potential encoding issues
        try:
            packet_str = data.decode('utf-8', errors='ignore')
        except:
            packet_str = data.decode('latin-1', errors='ignore')
        
        # Look for Shelly-specific indicators in the packet
        # Shelly devices typically include their device ID, model, or "shelly" in broadcasts
        packet_lower = packet_str.lower()
        
        if not any(indicator in packet_lower for indicator in ['shelly', 'shellyplus', 'coiot']):
            # Not a Shelly device packet
            return None
        
        logger.debug(f"Potential Shelly CoIoT packet from {source_ip}: {packet_str[:200]}...")
        
        # Try to parse as JSON if possible
        device_info = None
        try:
            # Look for JSON-like structures in the packet
            json_start = packet_str.find('{')
            json_end = packet_str.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = packet_str[json_start:json_end]
                parsed_data = json.loads(json_str)
                device_info = _extract_device_info_from_json(parsed_data, source_ip)
        except:
            # Not valid JSON, try to extract info from raw text
            device_info = _extract_device_info_from_text(packet_str, source_ip)
        
        # If we couldn't parse specific info, create a basic device entry
        if not device_info:
            device_info = _create_basic_shelly_device(source_ip, packet_str)
        
        return device_info
        
    except Exception as e:
        logger.debug(f"Error parsing CoIoT packet from {source_ip}: {e}")
        return None

def _extract_device_info_from_json(data: dict, source_ip: str) -> Optional[Dict[str, Any]]:
    """Extract device information from parsed JSON CoIoT data."""
    try:
        # Common Shelly JSON fields to look for
        device_id = data.get('id') or data.get('device_id') or data.get('mac')
        device_name = data.get('name') or data.get('device_name')
        model = data.get('model') or data.get('type') or data.get('device_type')
        mac_address = data.get('mac') or data.get('mac_address')
        firmware = data.get('fw') or data.get('firmware') or data.get('fw_ver')
        
        # Determine device generation and model from available data
        generation = "gen1"
        device_model = "shelly-plug"
        
        if model:
            model_lower = str(model).lower()
            if 'plus' in model_lower:
                generation = "gen2"
                device_model = "shellyplus-plug-us"
            elif 'pro' in model_lower:
                generation = "gen2"
                device_model = "shellypro"
        
        # Generate device ID if not provided
        if not device_id:
            if mac_address:
                device_id = f"shelly_{mac_address.replace(':', '').lower()}"
            else:
                device_id = f"shelly_{source_ip.replace('.', '_')}"
        
        # Generate display name
        if not device_name:
            if generation == "gen2":
                device_name = "Shelly Plus Plug US"
            else:
                device_name = "Shelly Plug"
        
        device_info = {
            "id": device_id,
            "name": device_name,
            "ip": source_ip,
            "type": "wifi",
            "model": device_model,
            "manufacturer": "Shelly",
            "generation": generation,
            "discovered_via": "coiot",
            "capabilities": {
                "on_off": True,
                "power_monitoring": True,
                "energy_monitoring": True,
                "temperature_monitoring": True
            }
        }
        
        # Add optional fields if available
        if mac_address:
            device_info["mac_address"] = mac_address
        if firmware:
            device_info["firmware_version"] = firmware
        
        # Add any additional status information
        if "switch:0" in data or "relay" in data:
            device_info["supports_switching"] = True
        if "power" in data or "apower" in data:
            device_info["supports_power_monitoring"] = True
        
        return device_info
        
    except Exception as e:
        logger.debug(f"Error extracting info from JSON: {e}")
        return None

def _extract_device_info_from_text(packet_str: str, source_ip: str) -> Optional[Dict[str, Any]]:
    """Extract device information from raw text CoIoT packet."""
    try:
        packet_lower = packet_str.lower()
        
        # Look for common Shelly indicators and model information
        generation = "gen1"
        device_model = "shelly-plug"
        device_name = "Shelly Plug"
        
        if 'plus' in packet_lower:
            generation = "gen2"
            device_model = "shellyplus-plug-us"
            device_name = "Shelly Plus Plug US"
        elif 'pro' in packet_lower:
            generation = "gen2"
            device_model = "shellypro"
            device_name = "Shelly Pro"
        
        # Try to extract MAC address (common formats: XX:XX:XX:XX:XX:XX or XXXXXXXXXXXX)
        import re
        mac_patterns = [
            r'([0-9a-f]{2}[:-]){5}[0-9a-f]{2}',  # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
            r'[0-9a-f]{12}',  # XXXXXXXXXXXX
        ]
        
        mac_address = None
        for pattern in mac_patterns:
            match = re.search(pattern, packet_lower)
            if match:
                mac_address = match.group(0)
                break
        
        # Generate device ID
        if mac_address:
            device_id = f"shelly_{mac_address.replace(':', '').replace('-', '').lower()}"
        else:
            device_id = f"shelly_{source_ip.replace('.', '_')}"
        
        device_info = {
            "id": device_id,
            "name": device_name,
            "ip": source_ip,
            "type": "wifi",
            "model": device_model,
            "manufacturer": "Shelly",
            "generation": generation,
            "discovered_via": "coiot",
            "capabilities": {
                "on_off": True,
                "power_monitoring": True,
                "energy_monitoring": True,
                "temperature_monitoring": True
            }
        }
        
        if mac_address:
            device_info["mac_address"] = mac_address
        
        return device_info
        
    except Exception as e:
        logger.debug(f"Error extracting info from text: {e}")
        return None

def _create_basic_shelly_device(source_ip: str, packet_str: str) -> Dict[str, Any]:
    """Create a basic Shelly device entry when detailed parsing fails."""
    device_id = f"shelly_{source_ip.replace('.', '_')}"
    
    # Make educated guess about generation based on packet content
    generation = "gen2" if 'plus' in packet_str.lower() else "gen1"
    model = "shellyplus-plug-us" if generation == "gen2" else "shelly-plug"
    name = "Shelly Plus Plug US" if generation == "gen2" else "Shelly Plug"
    
    return {
        "id": device_id,
        "name": name,
        "ip": source_ip,
        "type": "wifi",
        "model": model,
        "manufacturer": "Shelly",
        "generation": generation,
        "discovered_via": "coiot",
        "capabilities": {
            "on_off": True,
            "power_monitoring": True,
            "energy_monitoring": True,
            "temperature_monitoring": True
        }
    }

async def discover_wifi_devices() -> List[Dict[str, Any]]:
    """
    Discover Wi-Fi devices using multiple methods: CoIoT multicast, zeroconf, and subnet scanning.
    
    This function runs three discovery methods concurrently:
    1. Shelly CoIoT multicast listener (native protocol)
    2. Zeroconf/mDNS service discovery
    3. Subnet scanning with HTTP endpoint testing
    
    Returns:
        List of discovered Wi-Fi devices with id, name, ip, and type.
    """
    discovered_devices = []
    
    try:
        # Import zeroconf - handle gracefully if not available
        try:
            from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
            zeroconf_available = True
        except ImportError:
            logger.warning("zeroconf library not available. Install with: pip install zeroconf")
            zeroconf_available = False
        
        logger.info("Starting Wi-Fi device discovery...")
        
        # Run all discovery methods concurrently
        discovery_tasks = []
        
        # 1. Shelly CoIoT multicast discovery (primary method for Shelly devices)
        discovery_tasks.append(asyncio.create_task(discover_shelly_coiot()))
        
        # 2. Zeroconf discovery (if available)
        if zeroconf_available:
            discovery_tasks.append(asyncio.create_task(_discover_wifi_zeroconf()))
        
        # 3. Subnet scanning (fallback method)
        discovery_tasks.append(asyncio.create_task(discover_shelly_subnet_scan()))
        
        # Wait for all discovery methods to complete
        results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        
        # Process results from each discovery method
        coiot_devices = results[0] if not isinstance(results[0], Exception) else []
        if isinstance(results[0], Exception):
            logger.error(f"CoIoT discovery failed: {results[0]}")
        
        zeroconf_devices = []
        subnet_devices = []
        
        if zeroconf_available:
            zeroconf_devices = results[1] if not isinstance(results[1], Exception) else []
            if isinstance(results[1], Exception):
                logger.error(f"Zeroconf discovery failed: {results[1]}")
            
            subnet_devices = results[2] if not isinstance(results[2], Exception) else []
            if isinstance(results[2], Exception):
                logger.error(f"Subnet scan failed: {results[2]}")
        else:
            subnet_devices = results[1] if not isinstance(results[1], Exception) else []
            if isinstance(results[1], Exception):
                logger.error(f"Subnet scan failed: {results[1]}")
        
        # Merge results and remove duplicates based on IP address
        # Priority order: CoIoT > Zeroconf > Subnet scan
        seen_ips = set()
        all_devices = coiot_devices + zeroconf_devices + subnet_devices
        
        for device in all_devices:
            ip = device.get("ip")
            if ip and ip not in seen_ips:
                discovered_devices.append(device)
                seen_ips.add(ip)
            elif not ip:
                # Device without IP (shouldn't happen, but include anyway)
                discovered_devices.append(device)
        
        # Log discovery summary
        logger.info(f"Wi-Fi discovery completed:")
        logger.info(f"  CoIoT: {len(coiot_devices)} devices")
        logger.info(f"  Zeroconf: {len(zeroconf_devices)} devices")
        logger.info(f"  Subnet scan: {len(subnet_devices)} devices")
        logger.info(f"  Total unique: {len(discovered_devices)} devices")
        
    except Exception as e:
        logger.error(f"Wi-Fi discovery failed: {e}")
    
    return discovered_devices

async def discover_shelly_manual(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Manually discover/verify a Shelly device at a specific IP address.
    
    This function serves as the manual IP fallback mentioned in the requirements.
    It connects directly to the provided IP and tests for Shelly endpoints.
    
    Args:
        ip_address: The IP address to test for a Shelly device
    
    Returns:
        Device information dictionary if a Shelly device is found, None otherwise
    """
    try:
        import httpx
        
        logger.info(f"Testing manual IP {ip_address} for Shelly device...")
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            # Test Gen2 endpoint first (/rpc/Shelly.GetDeviceInfo)
            try:
                response = await client.get(f"http://{ip_address}/rpc/Shelly.GetDeviceInfo")
                if response.status_code == 200:
                    device_info = response.json()
                    
                    # Extract device information from Gen2 API
                    device = {
                        "id": f"shellyplus_{ip_address.replace('.', '_')}",
                        "name": device_info.get("name", "Shelly Plus Plug US"),
                        "ip": ip_address,
                        "type": "wifi",
                        "model": device_info.get("model", "shellyplus-plug-us"),
                        "manufacturer": "Shelly",
                        "generation": "gen2",
                        "discovered_via": "manual",
                        "capabilities": {
                            "on_off": True,
                            "power_monitoring": True,
                            "energy_monitoring": True,
                            "temperature_monitoring": True
                        }
                    }
                    
                    # Add additional info if available
                    if "mac" in device_info:
                        device["mac_address"] = device_info["mac"]
                    if "fw_ver" in device_info:
                        device["firmware_version"] = device_info["fw_ver"]
                    if "app" in device_info:
                        device["app_name"] = device_info["app"]
                    
                    logger.info(f"Found Shelly Gen2 device manually at {ip_address}: {device['name']}")
                    return device
                    
            except Exception as e:
                logger.debug(f"Gen2 test failed for {ip_address}: {e}")
            
            # Test Gen1 endpoint (/settings)
            try:
                response = await client.get(f"http://{ip_address}/settings")
                if response.status_code == 200:
                    device_info = response.json()
                    
                    if isinstance(device_info, dict) and ("device" in device_info or "name" in device_info):
                        # Extract device information from Gen1 API
                        device = {
                            "id": f"shelly_{ip_address.replace('.', '_')}",
                            "name": device_info.get("name", "Shelly Plug"),
                            "ip": ip_address,
                            "type": "wifi",
                            "model": device_info.get("device", {}).get("type", "shelly-plug"),
                            "manufacturer": "Shelly",
                            "generation": "gen1",
                            "discovered_via": "manual",
                            "capabilities": {
                                "on_off": True,
                                "power_monitoring": True,
                                "energy_monitoring": True,
                                "temperature_monitoring": True
                            }
                        }
                        
                        # Add additional info if available
                        if "mac" in device_info:
                            device["mac_address"] = device_info["mac"]
                        if "fw" in device_info:
                            device["firmware_version"] = device_info["fw"]
                        
                        logger.info(f"Found Shelly Gen1 device manually at {ip_address}: {device['name']}")
                        return device
                        
            except Exception as e:
                logger.debug(f"Gen1 test failed for {ip_address}: {e}")
        
        logger.info(f"No Shelly device found at {ip_address}")
        return None
        
    except Exception as e:
        logger.error(f"Manual discovery failed for {ip_address}: {e}")
        return None

async def _discover_wifi_with_fallback() -> List[Dict[str, Any]]:
    """
    Discover Wi-Fi devices with fallback to manual discovery of known devices.
    Uses manual discovery directly to avoid timeout issues.
    """
    discovered_devices = []
    
    try:
        # Start with manual discovery of common device IPs
        logger.info("Starting manual discovery of common device IPs...")
        
        # Common device IPs to check manually
        manual_ips = ["10.0.0.86", "192.168.1.86", "192.168.0.86"]
        
        for ip in manual_ips:
            try:
                device = await discover_shelly_manual(ip)
                if device:
                    discovered_devices.append(device)
                    logger.info(f"Found device via manual discovery: {ip}")
            except Exception as e:
                logger.debug(f"Manual discovery failed for {ip}: {e}")
        
        # If we found devices via manual discovery, return them
        if discovered_devices:
            logger.info(f"Manual discovery found {len(discovered_devices)} devices")
            return discovered_devices
            
        # If no manual devices found, try the automated discovery (with short timeout)
        logger.info("No manual devices found, trying automated discovery...")
        try:
            devices = await asyncio.wait_for(discover_wifi_devices(), timeout=5.0)
            discovered_devices.extend(devices)
        except asyncio.TimeoutError:
            logger.warning("Automated discovery timed out")
        except Exception as e:
            logger.warning(f"Automated discovery failed: {e}")
        
    except Exception as e:
        logger.error(f"Wi-Fi discovery with fallback failed: {e}")
    
    return discovered_devices

async def _discover_wifi_zeroconf() -> List[Dict[str, Any]]:
    """
    Discover Wi-Fi devices using zeroconf (mDNS/Bonjour).
    This is the original zeroconf-based discovery method.
    """
    discovered_devices = []
    
    try:
        from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
        
        logger.info("Starting zeroconf Wi-Fi device discovery...")
        
        class SmartDeviceListener(ServiceListener):
            def __init__(self):
                self.devices = []
            
            def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                try:
                    info = zc.get_service_info(type_, name)
                    if info and info.parsed_addresses():
                        ip_address = str(info.parsed_addresses()[0])
                        device_name_lower = name.lower()
                        
                        # Check for Shelly devices
                        if 'shelly' in device_name_lower:
                            device_id = name.split('.')[0].lower()
                            if not device_id.startswith('shelly'):
                                device_id = f"shelly_{device_id}"
                            
                            # Determine device type based on name
                            device_type = "switch"
                            if 'plug' in device_name_lower:
                                device_type = "plug"
                            elif 'dimmer' in device_name_lower:
                                device_type = "dimmer"
                            
                            device = {
                                "id": device_id,
                                "name": f"Shelly {device_type.title()}",
                                "ip": ip_address,
                                "type": "wifi",
                                "subtype": device_type,
                                "port": info.port if info.port else 80,
                                "discovered_via": "zeroconf",
                                "manufacturer": "Shelly"
                            }
                            
                            self.devices.append(device)
                            logger.info(f"Found Shelly device: {device['name']} at {ip_address}")
                        
                        # Check for TP-Link Kasa devices
                        elif 'kasa' in device_name_lower or 'tp-link' in device_name_lower or info.port == 9999:
                            device_id = f"kasa_{ip_address.replace('.', '_')}"
                            
                            device = {
                                "id": device_id,
                                "name": f"TP-Link Kasa Device",
                                "ip": ip_address,
                                "type": "wifi",
                                "subtype": "plug",
                                "port": info.port if info.port else 9999,
                                "discovered_via": "zeroconf",
                                "manufacturer": "TP-Link"
                            }
                            
                            self.devices.append(device)
                            logger.info(f"Found Kasa device at {ip_address}")
                        
                        # Check for other smart devices (generic detection)
                        else:
                            # Look for common smart device indicators
                            smart_indicators = ['smart', 'plug', 'switch', 'light', 'bulb', 'socket']
                            if any(indicator in device_name_lower for indicator in smart_indicators):
                                device_id = f"smart_{ip_address.replace('.', '_')}"
                                
                                device = {
                                    "id": device_id,
                                    "name": f"Smart Device ({name.split('.')[0]})",
                                    "ip": ip_address,
                                    "type": "wifi",
                                    "subtype": "unknown",
                                    "port": info.port if info.port else 80,
                                    "discovered_via": "zeroconf",
                                    "manufacturer": "Unknown"
                                }
                                
                                self.devices.append(device)
                                logger.info(f"Found generic smart device: {name} at {ip_address}")
                            
                except Exception as e:
                    logger.debug(f"Error processing service {name}: {e}")
            
            def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass
            
            def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass
        
        # Set up zeroconf discovery
        zeroconf = Zeroconf()
        listener = SmartDeviceListener()
        
        # Browse for multiple service types where smart devices typically appear
        service_types = [
            "_http._tcp.local.",     # HTTP services (Shelly, many others)
            "_tplink._tcp.local.",   # TP-Link specific
            "_device-info._tcp.local.", # Device info services
        ]
        
        browsers = []
        for service_type in service_types:
            try:
                browser = ServiceBrowser(zeroconf, service_type, listener)
                browsers.append(browser)
                logger.debug(f"Started browser for {service_type}")
            except Exception as e:
                logger.debug(f"Failed to start browser for {service_type}: {e}")
        
        # Wait for discovery with timeout
        await asyncio.sleep(5)  # Reduced from 15 seconds for better responsiveness
        
        # Clean up
        for browser in browsers:
            try:
                browser.cancel()
            except:
                pass
        zeroconf.close()
        
        discovered_devices = listener.devices
        logger.info(f"Zeroconf discovery completed. Found {len(discovered_devices)} devices.")
        
    except Exception as e:
        logger.error(f"Zeroconf discovery failed: {e}")
    
    return discovered_devices

async def discover_shelly_subnet_scan() -> List[Dict[str, Any]]:
    """
    Discover Shelly devices by scanning local subnet IP addresses.
    Tests each IP for Gen1 (/relay/0) and Gen2 (/rpc/Switch.GetStatus) endpoints.
    
    Returns:
        List of discovered Shelly devices with id, name, ip, model, and type.
    """
    discovered_devices = []
    
    try:
        import httpx
        import socket
        
        logger.info("Starting Shelly subnet scan...")
        
        # Simplified network detection - use socket method directly
        def get_local_networks():
            """Get local network ranges to scan - simplified version."""
            networks = []
            try:
                # Connect to a public DNS server to find our actual IP
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    
                if not local_ip.startswith('127.'):
                    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
                    networks.append(network)
                    logger.debug(f"Found network via socket method: {network}")
                    return networks
                        
            except Exception as e:
                logger.debug(f"Socket method failed: {e}")
            
            # Fallback to common private networks
            networks = [
                ipaddress.IPv4Network("10.0.0.0/24"),      # Common for home routers
                ipaddress.IPv4Network("192.168.1.0/24"),   # Very common for home routers  
                ipaddress.IPv4Network("192.168.0.0/24"),   # Common for home routers
            ]
            logger.debug("Using fallback networks")
            
            return networks
        
        async def test_shelly_device(ip_address: str) -> Optional[Dict[str, Any]]:
            """Test if an IP address hosts a Shelly device."""
            try:
                async with httpx.AsyncClient() as client:
                    # Test Gen2 endpoint first (/rpc/Switch.GetStatus?id=0)
                    try:
                        response = await client.get(
                            f"http://{ip_address}/rpc/Switch.GetStatus?id=0", 
                            timeout=3.0
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if isinstance(result, dict) and "id" in result and result.get("id") == 0:
                                # This is a Shelly Gen2 device
                                device = {
                                    "id": f"shellyplus_{ip_address.replace('.', '_')}",
                                    "name": "Shelly Plus Plug US",
                                    "ip": ip_address,
                                    "type": "wifi",
                                    "model": "shellyplus-plug-us",
                                    "manufacturer": "Shelly",
                                    "generation": "gen2",
                                    "discovered_via": "subnet_scan",
                                    "capabilities": {
                                        "on_off": True,
                                        "power_monitoring": True,
                                        "energy_monitoring": True,
                                        "temperature_monitoring": True
                                    }
                                }
                                logger.info(f"Found Shelly Gen2 device at {ip_address}")
                                return device
                    except httpx.HTTPStatusError:
                        pass  # Not a Gen2 device
                    except Exception:
                        pass  # Network error, continue testing
                    
                    # Test Gen1 endpoint (/relay/0)
                    try:
                        response = await client.get(f"http://{ip_address}/relay/0", timeout=3.0)
                        if response.status_code == 200:
                            result = response.json()
                            if isinstance(result, dict) and "ison" in result:
                                # This is a Shelly Gen1 device
                                device = {
                                    "id": f"shelly_{ip_address.replace('.', '_')}",
                                    "name": "Shelly Plug",
                                    "ip": ip_address,
                                    "type": "wifi",
                                    "model": "shelly-plug",
                                    "manufacturer": "Shelly",
                                    "generation": "gen1",
                                    "discovered_via": "subnet_scan",
                                    "capabilities": {
                                        "on_off": True,
                                        "power_monitoring": True,
                                        "energy_monitoring": True,
                                        "temperature_monitoring": True
                                    }
                                }
                                logger.info(f"Found Shelly Gen1 device at {ip_address}")
                                return device
                    except httpx.HTTPStatusError:
                        pass  # Not a Shelly device
                    except Exception:
                        pass  # Network error
                        
            except Exception as e:
                logger.debug(f"Error testing {ip_address}: {e}")
            
            return None
        
        # Get networks to scan
        networks = get_local_networks()
        
        # Generate IP addresses to test (simplified approach)
        test_ips = []
        for network in networks:
            network_base = str(network.network_address)
            
            # For 10.0.0.x network, focus on common device ranges
            if network_base.startswith("10.0.0"):
                # Test most likely device IP ranges first
                priority_ranges = [
                    range(80, 90),     # Focus on 80s where user's device is at 86
                    range(1, 20),      # Router and infrastructure: 1-19
                    range(50, 70),     # Common device range: 50-69
                ]
                
                for ip_range in priority_ranges:
                    for i in ip_range:
                        test_ips.append(f"10.0.0.{i}")
                        
            elif network_base.startswith("192.168"):
                # For 192.168.x.x networks, test common ranges
                base_parts = network_base.split('.')
                base = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}"
                for i in range(1, 50):  # Test first 50 IPs
                    test_ips.append(f"{base}.{i}")
        
        # Remove duplicates and limit to reasonable size
        test_ips = list(dict.fromkeys(test_ips))[:100]  # Limit to 100 IPs max
        logger.info(f"Testing {len(test_ips)} IP addresses for Shelly devices")
        
        # Test IPs concurrently with limited concurrency
        semaphore = asyncio.Semaphore(3)  # Conservative concurrency
        
        async def test_with_limit(ip):
            async with semaphore:
                return await test_shelly_device(ip)
        
        tasks = [test_with_limit(ip) for ip in test_ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful discoveries
        for result in results:
            if result and not isinstance(result, Exception):
                discovered_devices.append(result)
        
        logger.info(f"Subnet scan found {len(discovered_devices)} Shelly devices")
        
    except Exception as e:
        logger.error(f"Shelly subnet scan failed: {e}")
    
    return discovered_devices

async def discover_zwave_devices() -> List[Dict[str, Any]]:
    """
    Discover Z-Wave devices using available Z-Wave libraries.
    Prioritizes zwave-js-server-python, falls back to mock for development.
    
    Returns:
        List of discovered Z-Wave devices with id, name, node_id, and type.
    """
    discovered_devices = []
    
    try:
        logger.info("Starting Z-Wave device discovery...")
        
        # Try Z-Wave JS server first (real implementation)
        devices = await _try_zwavejs_discovery()
        
        # If no real devices found, try other methods
        if not devices:
            devices = await _try_openzwave_discovery()
            
        # Fallback to mock only if no real Z-Wave server is available
        if not devices:
            logger.info("No Z-Wave server available, using mock discovery for development")
            devices = await _try_mock_zwave_discovery()
            
        discovered_devices = devices
        logger.info(f"Z-Wave discovery completed. Found {len(discovered_devices)} devices.")
        
    except Exception as e:
        logger.error(f"Z-Wave discovery failed: {e}")
    
    return discovered_devices

async def _try_openzwave_discovery() -> List[Dict[str, Any]]:
    """Try discovering Z-Wave devices using python-openzwave."""
    try:
        # Import python-openzwave - handle gracefully if not available
        try:
            from openzwave.network import ZWaveNetwork
            from openzwave.option import ZWaveOption
        except ImportError:
            logger.debug("python-openzwave not available")
            return []
        
        logger.debug("Attempting Z-Wave discovery with python-openzwave")
        
        # This is a simplified example - real implementation would need proper setup
        # For now, return empty list as this requires hardware setup
        logger.info("python-openzwave available but requires Z-Wave controller setup")
        return []
        
    except Exception as e:
        logger.debug(f"python-openzwave discovery failed: {e}")
        return []

async def _try_zwavejs_discovery() -> List[Dict[str, Any]]:
    """Try discovering Z-Wave devices using zwave-js-server-python."""
    try:
        # Import zwave-js-server-python - handle gracefully if not available
        try:
            from zwave_js_server.client import Client as ZwaveClient
            from zwave_js_server.model.driver import Driver
            import aiohttp
        except ImportError:
            logger.debug("zwave-js-server-python not available")
            return []
        
        logger.debug("Attempting Z-Wave discovery with zwave-js-server-python")
        
        # Import registry functions to filter out existing devices
        from .registry import load_registry
        
        # Connect to Z-Wave JS server (default: ws://localhost:3000)
        ws_url = "ws://localhost:3000"
        discovered_devices = []
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Connecting to Z-Wave JS server at {ws_url}")
                
                async with ZwaveClient(ws_url, session) as client:
                    # Wait for driver to be ready
                    if not client.connected:
                        logger.warning("Z-Wave JS client not connected")
                        return []
                    
                    driver = client.driver
                    if not driver:
                        logger.warning("Z-Wave driver not available")
                        return []
                    
                    logger.info(f"Connected to Z-Wave JS server, driver ready: {driver.controller.is_ready}")
                    
                    # Get existing devices from registry to filter duplicates
                    existing_devices = await load_registry()
                    existing_node_ids = {
                        device.get('node_id') for device in existing_devices 
                        if device.get('type') == 'zwave' and device.get('node_id')
                    }
                    
                    # Get all nodes from the Z-Wave network
                    for node_id, node in driver.controller.nodes.items():
                        # Skip controller node (usually node 1) and already registered devices
                        if node_id == 1 or node_id in existing_node_ids:
                            continue
                        
                        # Skip nodes that are not ready or interviewed
                        if not node.ready:
                            logger.debug(f"Skipping node {node_id}: not ready")
                            continue
                        
                        # Create device entry
                        device_name = node.name or f"Z-Wave Device {node_id}"
                        if hasattr(node, 'device_class') and node.device_class:
                            device_name = f"{node.device_class.specific.label or 'Unknown'} (Node {node_id})"
                        
                        device = {
                            "id": f"zwave-{node_id}",
                            "name": device_name,
                            "type": "zwave", 
                            "node_id": node_id,
                            "manufacturer": getattr(node, 'manufacturer_id', 'Unknown'),
                            "product": getattr(node, 'product_id', 'Unknown'),
                            "discovered_via": "zwave-js-server"
                        }
                        
                        # Add additional metadata if available
                        if hasattr(node, 'manufacturer_name'):
                            device["manufacturer_name"] = node.manufacturer_name
                        if hasattr(node, 'product_name'):
                            device["product_name"] = node.product_name
                        if hasattr(node, 'firmware_version'):
                            device["firmware_version"] = node.firmware_version
                        
                        discovered_devices.append(device)
                        logger.info(f"Found Z-Wave device: {device_name} (Node {node_id})")
                
                logger.info(f"Z-Wave JS discovery found {len(discovered_devices)} new devices")
                return discovered_devices
                
        except aiohttp.ClientError as e:
            logger.warning(f"Cannot connect to Z-Wave JS server at {ws_url}: {e}")
            logger.info("Make sure Z-Wave JS server is running (e.g., 'npx @zwave-js/server')")
            return []
        except Exception as e:
            logger.warning(f"Z-Wave JS server connection failed: {e}")
            return []
        
    except Exception as e:
        logger.debug(f"zwave-js-server discovery failed: {e}")
        return []

async def _try_mock_zwave_discovery() -> List[Dict[str, Any]]:
    """Mock Z-Wave discovery for development/testing purposes."""
    try:
        logger.debug("Mock Z-Wave discovery disabled - no mock devices returned")
        
        # Return empty list - no mock devices
        return []
        
    except Exception as e:
        logger.debug(f"Mock Z-Wave discovery failed: {e}")
        return []

async def discover_all_devices() -> Dict[str, List[Dict[str, Any]]]:
    """
    Discover all devices from Wi-Fi, Z-Wave, and Govee sources.
    Runs all discovery methods concurrently with timeouts.
    
    Returns:
        Dictionary with 'wifi', 'zwave', and 'govee' keys containing respective device lists.
    """
    logger.info("Starting comprehensive device discovery...")
    
    try:
        # Import Govee discovery - handle gracefully if not available
        try:
            from .govee import discover_govee_devices
            govee_available = True
        except ImportError:
            logger.debug("Govee discovery module not available")
            govee_available = False
        
        # Run all discovery methods concurrently with timeouts
        wifi_task = asyncio.create_task(
            asyncio.wait_for(_discover_wifi_with_fallback(), timeout=WIFI_DISCOVERY_TIMEOUT)
        )
        zwave_task = asyncio.create_task(
            asyncio.wait_for(discover_zwave_devices(), timeout=ZWAVE_DISCOVERY_TIMEOUT)
        )
        
        # Only add Govee task if available
        if govee_available:
            govee_task = asyncio.create_task(
                asyncio.wait_for(discover_govee_devices(), timeout=GOVEE_DISCOVERY_TIMEOUT)
            )
            # Wait for all to complete (or timeout)
            wifi_devices, zwave_devices, govee_devices = await asyncio.gather(
                wifi_task, zwave_task, govee_task, return_exceptions=True
            )
        else:
            # Skip Govee discovery
            wifi_devices, zwave_devices = await asyncio.gather(
                wifi_task, zwave_task, return_exceptions=True
            )
            govee_devices = []
        
        # Handle exceptions from discovery methods
        if isinstance(wifi_devices, Exception):
            logger.error(f"Wi-Fi discovery timed out or failed: {wifi_devices}")
            wifi_devices = []
        
        if isinstance(zwave_devices, Exception):
            logger.error(f"Z-Wave discovery timed out or failed: {zwave_devices}")
            zwave_devices = []
            
        if isinstance(govee_devices, Exception):
            logger.error(f"Govee discovery timed out or failed: {govee_devices}")
            govee_devices = []
        
        total_devices = len(wifi_devices) + len(zwave_devices) + len(govee_devices)
        logger.info(f"Discovery completed: {len(wifi_devices)} Wi-Fi + {len(zwave_devices)} Z-Wave + {len(govee_devices)} Govee = {total_devices} total")
        
        return {
            "wifi": wifi_devices,
            "zwave": zwave_devices,
            "govee": govee_devices
        }
        
    except Exception as e:
        logger.error(f"Device discovery failed: {e}")
        return {"wifi": [], "zwave": [], "govee": []}

def merge_discovered_devices(discovery_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge Wi-Fi, Z-Wave, and Govee discovery results into a single list.
    
    Args:
        discovery_results: Dictionary with 'wifi', 'zwave', and 'govee' device lists
    
    Returns:
        Merged list of all discovered devices
    """
    merged_devices = []
    
    # Add Wi-Fi devices
    for device in discovery_results.get("wifi", []):
        merged_devices.append(device)
    
    # Add Z-Wave devices
    for device in discovery_results.get("zwave", []):
        merged_devices.append(device)
        
    # Add Govee devices
    for device in discovery_results.get("govee", []):
        merged_devices.append(device)
    
    logger.info(f"Merged {len(merged_devices)} discovered devices")
    return merged_devices
