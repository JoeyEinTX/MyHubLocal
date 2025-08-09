"""
Govee device discovery and control module.
Provides async functions to discover and control Govee LED devices locally.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import socket

logger = logging.getLogger(__name__)

# Govee discovery settings
GOVEE_DISCOVERY_TIMEOUT = 5
GOVEE_SCAN_MESSAGE = b'{"msg":{"cmd":"scan","data":{"account_topic":"reserve"}}}\r\n'
GOVEE_UDP_PORT = 4003

async def discover_govee_devices() -> List[Dict[str, Any]]:
    """
    Discover Govee devices on the local network using UDP broadcast.
    Specifically targets H7058 and other network-capable Govee devices.
    
    Returns:
        List of discovered Govee devices with id, name, ip, and device info.
    """
    discovered_devices = []
    
    try:
        logger.info("Starting Govee device discovery...")
        
        # Use asyncio.timeout for better async handling
        import asyncio
        
        async def _do_govee_scan():
            import socket
            import json
            
            # Create UDP socket for discovery
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(0.5)  # Short timeout for non-blocking
            
            found_devices = []
            
            try:
                # Send broadcast discovery message
                broadcast_address = ('255.255.255.255', GOVEE_UDP_PORT)
                sock.sendto(GOVEE_SCAN_MESSAGE, broadcast_address)
                logger.debug(f"Sent Govee discovery broadcast to {broadcast_address}")
                
                # Listen for responses with multiple attempts
                for attempt in range(10):  # 10 attempts over 5 seconds
                    try:
                        await asyncio.sleep(0.5)  # Wait between attempts
                        
                        # Try to receive data (non-blocking due to timeout)
                        try:
                            data, addr = sock.recvfrom(1024)
                            response_data = data.decode('utf-8').strip()
                            
                            logger.info(f"Received Govee response from {addr[0]}: {response_data}")
                            
                            # Parse Govee response
                            device_info = await _parse_govee_response(response_data, addr[0])
                            if device_info:
                                found_devices.append(device_info)
                                logger.info(f"✅ Found Govee device: {device_info['name']} at {addr[0]}")
                                
                        except socket.timeout:
                            continue  # Normal - keep trying
                        except UnicodeDecodeError:
                            logger.debug(f"Received non-UTF8 data from {addr[0] if 'addr' in locals() else 'unknown'}")
                            continue
                            
                    except Exception as e:
                        logger.debug(f"Error in attempt {attempt}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error in Govee UDP discovery: {e}")
            finally:
                sock.close()
                
            return found_devices
        
        # Run the scan with a timeout
        try:
            discovered_devices = await asyncio.wait_for(_do_govee_scan(), timeout=GOVEE_DISCOVERY_TIMEOUT)
        except asyncio.TimeoutError:
            logger.warning("Govee discovery timed out")
            discovered_devices = []
            
        # Try alternative discovery method if UDP fails
        if not discovered_devices:
            logger.info("UDP discovery failed, trying network scan...")
            discovered_devices = await _try_govee_network_scan()
            
        logger.info(f"Govee discovery completed. Found {len(discovered_devices)} devices.")
        
    except Exception as e:
        logger.error(f"Govee discovery failed: {e}")
        import traceback
        logger.debug(f"Govee discovery traceback: {traceback.format_exc()}")
    
    return discovered_devices

async def _parse_govee_response(response_data: str, ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Parse Govee device response and extract device information.
    
    Args:
        response_data: JSON response from Govee device
        ip_address: IP address of the responding device
        
    Returns:
        Dictionary with device information or None if parsing fails
    """
    try:
        import json
        
        # Parse JSON response
        response = json.loads(response_data)
        
        # Extract device information
        msg = response.get('msg', {})
        data = msg.get('data', {})
        
        device_name = data.get('device', 'Unknown Govee Device')
        device_model = data.get('sku', 'Unknown Model')
        device_ip = data.get('ip', ip_address)
        
        # Create device ID from IP and model
        device_id = f"govee_{device_ip.replace('.', '_')}_{device_model.lower()}"
        
        # Determine device type based on model
        device_type = "led_strip"
        if "H7058" in device_model:
            device_type = "led_strip"
            device_name = f"Govee LED Strip {device_model}"
        elif "bulb" in device_model.lower():
            device_type = "bulb"
            device_name = f"Govee Bulb {device_model}"
        
        device_info = {
            "id": device_id,
            "name": device_name,
            "ip": device_ip,
            "type": "govee",
            "subtype": device_type,
            "model": device_model,
            "manufacturer": "Govee",
            "discovered_via": "govee_udp",
            "capabilities": {
                "on_off": True,
                "brightness": True,
                "color": True,
                "color_temp": True
            }
        }
        
        # Add model-specific capabilities
        if "H7058" in device_model:
            device_info["capabilities"].update({
                "effects": True,
                "music_sync": True,
                "segments": True
            })
        
        return device_info
        
    except json.JSONDecodeError:
        logger.debug(f"Invalid JSON response from {ip_address}: {response_data}")
        return None
    except Exception as e:
        logger.debug(f"Error parsing Govee response from {ip_address}: {e}")
        return None

async def send_govee_command(device_ip: str, command_payload: Dict[str, Any]) -> bool:
    """
    Send a command to a Govee device via UDP.
    
    Args:
        device_ip: IP address of the Govee device
        command_payload: Dictionary containing the command to send
    
    Returns:
        bool: True if command was sent successfully, False otherwise
    """
    try:
        import json
        
        logger.info(f"Sending Govee command to {device_ip}: {command_payload}")
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        try:
            # Format command message
            message = {
                "msg": {
                    "cmd": "turn",
                    "data": command_payload
                }
            }
            
            message_json = json.dumps(message) + '\r\n'
            message_bytes = message_json.encode('utf-8')
            
            # Send command
            sock.sendto(message_bytes, (device_ip, GOVEE_UDP_PORT))
            logger.debug(f"Sent command to {device_ip}: {message_json.strip()}")
            
            # Try to receive acknowledgment (optional)
            try:
                response, _ = sock.recvfrom(1024)
                logger.debug(f"Govee response: {response.decode('utf-8').strip()}")
            except socket.timeout:
                # No response is okay for many Govee commands
                pass
            
            return True
            
        finally:
            sock.close()
            
    except Exception as e:
        logger.error(f"Error sending Govee command to {device_ip}: {e}")
        return False

async def get_govee_status(device_ip: str) -> Optional[Dict[str, Any]]:
    """
    Get current status of a Govee device.
    
    Args:
        device_ip: IP address of the Govee device
    
    Returns:
        Dictionary with device status or None if failed
    """
    try:
        import json
        
        # Create status request
        status_request = {
            "msg": {
                "cmd": "devStatus",
                "data": {}
            }
        }
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        
        try:
            # Send status request
            message = json.dumps(status_request) + '\r\n'
            sock.sendto(message.encode('utf-8'), (device_ip, GOVEE_UDP_PORT))
            
            # Receive response
            response, _ = sock.recvfrom(1024)
            response_data = json.loads(response.decode('utf-8'))
            
            # Parse status response
            data = response_data.get('msg', {}).get('data', {})
            
            return {
                "is_on": data.get("onOff", 0) == 1,
                "brightness": data.get("brightness", 0),
                "color": {
                    "r": data.get("color", {}).get("r", 0),
                    "g": data.get("color", {}).get("g", 0),
                    "b": data.get("color", {}).get("b", 0)
                },
                "color_temp": data.get("colorTem", 0)
            }
            
        finally:
            sock.close()
            
    except Exception as e:
        logger.error(f"Error getting Govee status from {device_ip}: {e}")
        return None

async def _try_govee_network_scan() -> List[Dict[str, Any]]:
    """
    Alternative Govee discovery method using network scanning.
    Scans common IP ranges for devices responding to Govee commands.
    """
    discovered_devices = []
    
    try:
        import asyncio
        import socket
        import json
        
        logger.info("Starting Govee network scan...")
        
        # Get local network range
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Extract network base (assumes /24 subnet)
        ip_parts = local_ip.split('.')
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        logger.debug(f"Scanning network {network_base}.x for Govee devices")
        
        # Test a smaller range first (common device IPs)
        test_ips = [
            f"{network_base}.{i}" for i in range(100, 201, 10)  # .100, .110, .120, etc.
        ]
        
        async def test_govee_ip(ip_address):
            try:
                # Quick test - try to send a status request
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1.0)
                
                status_request = {
                    "msg": {
                        "cmd": "devStatus", 
                        "data": {}
                    }
                }
                
                message = json.dumps(status_request) + '\r\n'
                sock.sendto(message.encode('utf-8'), (ip_address, GOVEE_UDP_PORT))
                
                # If we get any response, it might be a Govee device
                try:
                    response, _ = sock.recvfrom(1024)
                    response_text = response.decode('utf-8')
                    
                    if 'govee' in response_text.lower() or 'led' in response_text.lower():
                        # Create a generic Govee device entry
                        device = {
                            "id": f"govee_{ip_address.replace('.', '_')}",
                            "name": f"Govee Device (H7058)",
                            "ip": ip_address,
                            "type": "govee",
                            "subtype": "led_strip",
                            "model": "H7058",
                            "manufacturer": "Govee",
                            "discovered_via": "network_scan",
                            "capabilities": {
                                "on_off": True,
                                "brightness": True,
                                "color": True,
                                "color_temp": True,
                                "effects": True
                            }
                        }
                        
                        logger.info(f"Found potential Govee device at {ip_address}")
                        return device
                        
                except socket.timeout:
                    pass  # No response
                    
                sock.close()
                
            except Exception as e:
                logger.debug(f"Error testing {ip_address}: {e}")
                
            return None
        
        # Test IPs concurrently (but limit concurrency)
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent tests
        
        async def test_with_limit(ip):
            async with semaphore:
                return await test_govee_ip(ip)
        
        tasks = [test_with_limit(ip) for ip in test_ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful discoveries
        for result in results:
            if result and not isinstance(result, Exception):
                discovered_devices.append(result)
        
        logger.info(f"Network scan found {len(discovered_devices)} potential Govee devices")
        
    except Exception as e:
        logger.error(f"Network scan failed: {e}")
    
    return discovered_devices
