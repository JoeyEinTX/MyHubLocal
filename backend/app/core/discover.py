"""
Device discovery module for Wi-Fi and Z-Wave devices.
Provides async functions to scan for Shelly plugs and Z-Wave devices.
"""
import asyncio
import logging
import socket
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Discovery timeouts in seconds
WIFI_DISCOVERY_TIMEOUT = 5
ZWAVE_DISCOVERY_TIMEOUT = 5

async def discover_wifi_devices() -> List[Dict[str, Any]]:
    """
    Discover Wi-Fi devices using zeroconf, specifically looking for Shelly devices.
    Scans _http._tcp.local. services for Shelly plugs and switches.
    
    Returns:
        List of discovered Wi-Fi devices with id, name, ip, and type.
    """
    discovered_devices = []
    
    try:
        # Import zeroconf - handle gracefully if not available
        try:
            from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
        except ImportError:
            logger.warning("zeroconf library not available. Install with: pip install zeroconf")
            return []
        
        logger.info("Starting Wi-Fi device discovery...")
        
        class ShellyDeviceListener(ServiceListener):
            def __init__(self):
                self.devices = []
            
            def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                try:
                    info = zc.get_service_info(type_, name)
                    if info and info.parsed_addresses():
                        # Check if this looks like a Shelly device
                        device_name = name.lower()
                        if 'shelly' in device_name or 'shellyplug' in device_name:
                            ip_address = str(info.parsed_addresses()[0])
                            
                            # Extract device ID from service name
                            device_id = name.split('.')[0].lower()
                            if not device_id.startswith('shelly'):
                                device_id = f"shelly_{device_id}"
                            
                            # Determine device type based on name
                            device_type = "switch"
                            if 'plug' in device_name:
                                device_type = "plug"
                            elif 'dimmer' in device_name:
                                device_type = "dimmer"
                            
                            # Create device entry
                            device = {
                                "id": device_id,
                                "name": f"Shelly {device_type.title()}",
                                "ip": ip_address,
                                "type": "wifi",
                                "subtype": device_type,
                                "port": info.port if info.port else 80,
                                "discovered_via": "zeroconf"
                            }
                            
                            self.devices.append(device)
                            logger.info(f"Found Shelly device: {device['name']} at {ip_address}")
                            
                except Exception as e:
                    logger.debug(f"Error processing service {name}: {e}")
            
            def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass
            
            def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                pass
        
        # Set up zeroconf discovery
        zeroconf = Zeroconf()
        listener = ShellyDeviceListener()
        
        # Browse for HTTP services (where Shelly devices typically appear)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        
        # Wait for discovery with timeout
        await asyncio.sleep(WIFI_DISCOVERY_TIMEOUT)
        
        # Clean up
        browser.cancel()
        zeroconf.close()
        
        discovered_devices = listener.devices
        logger.info(f"Wi-Fi discovery completed. Found {len(discovered_devices)} devices.")
        
    except Exception as e:
        logger.error(f"Wi-Fi discovery failed: {e}")
    
    return discovered_devices

async def discover_zwave_devices() -> List[Dict[str, Any]]:
    """
    Discover Z-Wave devices using available Z-Wave libraries.
    Attempts to use python-openzwave or zwave-js-server-python.
    
    Returns:
        List of discovered Z-Wave devices with id, name, node_id, and type.
    """
    discovered_devices = []
    
    try:
        logger.info("Starting Z-Wave device discovery...")
        
        # Try different Z-Wave libraries in order of preference
        devices = await _try_openzwave_discovery()
        if not devices:
            devices = await _try_zwavejs_discovery()
        if not devices:
            devices = await _try_mock_zwave_discovery()  # Fallback for development
            
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
            import zwave_js_server
        except ImportError:
            logger.debug("zwave-js-server-python not available")
            return []
        
        logger.debug("Attempting Z-Wave discovery with zwave-js-server-python")
        
        # This would connect to Z-Wave JS server
        # For now, return empty list as this requires Z-Wave JS server setup
        logger.info("zwave-js-server-python available but requires Z-Wave JS server")
        return []
        
    except Exception as e:
        logger.debug(f"zwave-js-server discovery failed: {e}")
        return []

async def _try_mock_zwave_discovery() -> List[Dict[str, Any]]:
    """Mock Z-Wave discovery for development/testing purposes."""
    try:
        logger.debug("Using mock Z-Wave discovery for development")
        
        # Simulate some Z-Wave devices for development
        mock_devices = [
            {
                "id": "zwave_node_2",
                "name": "Z-Wave Light Switch",
                "node_id": 2,
                "type": "zwave",
                "subtype": "switch",
                "manufacturer": "Aeotec",
                "product": "Smart Switch 6",
                "discovered_via": "mock"
            },
            {
                "id": "zwave_node_3", 
                "name": "Z-Wave Motion Sensor",
                "node_id": 3,
                "type": "zwave",
                "subtype": "sensor",
                "manufacturer": "Aeotec",
                "product": "MultiSensor 6",
                "discovered_via": "mock"
            }
        ]
        
        # Simulate discovery delay
        await asyncio.sleep(1)
        
        logger.info("Mock Z-Wave discovery returned sample devices")
        return mock_devices
        
    except Exception as e:
        logger.debug(f"Mock Z-Wave discovery failed: {e}")
        return []

async def discover_all_devices() -> Dict[str, List[Dict[str, Any]]]:
    """
    Discover all devices from both Wi-Fi and Z-Wave sources.
    Runs both discovery methods concurrently with timeouts.
    
    Returns:
        Dictionary with 'wifi' and 'zwave' keys containing respective device lists.
    """
    logger.info("Starting comprehensive device discovery...")
    
    try:
        # Run both discovery methods concurrently with timeouts
        wifi_task = asyncio.create_task(
            asyncio.wait_for(discover_wifi_devices(), timeout=WIFI_DISCOVERY_TIMEOUT)
        )
        zwave_task = asyncio.create_task(
            asyncio.wait_for(discover_zwave_devices(), timeout=ZWAVE_DISCOVERY_TIMEOUT)
        )
        
        # Wait for both to complete (or timeout)
        wifi_devices, zwave_devices = await asyncio.gather(
            wifi_task, zwave_task, return_exceptions=True
        )
        
        # Handle exceptions from discovery methods
        if isinstance(wifi_devices, Exception):
            logger.error(f"Wi-Fi discovery timed out or failed: {wifi_devices}")
            wifi_devices = []
        
        if isinstance(zwave_devices, Exception):
            logger.error(f"Z-Wave discovery timed out or failed: {zwave_devices}")
            zwave_devices = []
        
        total_devices = len(wifi_devices) + len(zwave_devices)
        logger.info(f"Discovery completed: {len(wifi_devices)} Wi-Fi + {len(zwave_devices)} Z-Wave = {total_devices} total")
        
        return {
            "wifi": wifi_devices,
            "zwave": zwave_devices
        }
        
    except Exception as e:
        logger.error(f"Device discovery failed: {e}")
        return {"wifi": [], "zwave": []}

def merge_discovered_devices(discovery_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge Wi-Fi and Z-Wave discovery results into a single list.
    
    Args:
        discovery_results: Dictionary with 'wifi' and 'zwave' device lists
    
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
    
    logger.info(f"Merged {len(merged_devices)} discovered devices")
    return merged_devices
