"""
Device protocol handlers for different smart home device types.
Provides async communication functions for Wi-Fi, Z-Wave, and Govee devices.
"""
import asyncio
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def _detect_shelly_generation(device_ip: str) -> str:
    """
    Detect whether a Shelly device is Gen1 or Gen2 by testing endpoints.
    
    Args:
        device_ip: IP address of the Shelly device
    
    Returns:
        str: "gen1" or "gen2" based on device response
    """
    try:
        async with httpx.AsyncClient() as client:
            # Try Gen2 status endpoint first
            try:
                response = await client.get(f"http://{device_ip}/rpc/Switch.GetStatus?id=0", timeout=3.0)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "id" in result and result.get("id") == 0:
                        logger.debug(f"Device {device_ip} detected as Gen2 (RPC API)")
                        return "gen2"
            except:
                pass
            
            # Try Gen1 status endpoint as fallback
            try:
                response = await client.get(f"http://{device_ip}/relay/0", timeout=3.0)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict) and "ison" in result:
                        logger.debug(f"Device {device_ip} detected as Gen1 (legacy API)")
                        return "gen1"
            except:
                pass
                
    except Exception as e:
        logger.debug(f"Error detecting Shelly generation for {device_ip}: {e}")
    
    # Default to Gen1 if detection fails
    logger.debug(f"Device {device_ip} defaulting to Gen1 (detection failed)")
    return "gen1"

async def send_shelly_command(device_ip: str, command_payload: Dict[str, Any]) -> bool:
    """
    Send a command to a Shelly device via HTTP API.
    Supports both Gen1 (/relay/0) and Gen2 (/rpc/Switch.Set) devices.
    
    Args:
        device_ip: IP address of the Shelly device
        command_payload: Dictionary containing the command to send
                        Must contain "on" key with boolean value
    
    Returns:
        bool: True if command was successful and device state matches expected,
              False otherwise
    """
    try:
        # Check if command payload contains the required "on" key
        if "on" not in command_payload:
            logger.error(f"Command payload missing 'on' key: {command_payload}")
            return False
        
        command_state = command_payload["on"]
        
        # First, detect if this is a Gen1 or Gen2 Shelly device
        device_generation = await _detect_shelly_generation(device_ip)
        
        if device_generation == "gen2":
            # Gen2 RPC API: /rpc/Switch.Set?id=0&on=true/false
            url = f"http://{device_ip}/rpc/Switch.Set?id=0&on={str(command_state).lower()}"
            logger.info(f"Sending Shelly Gen2 command to {device_ip}: on={command_state}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                
                # Gen2 devices return a simple response, verify with status check
                await asyncio.sleep(0.1)  # Brief delay for state change
                verification = await get_shelly_status(device_ip)
                
                if verification:
                    device_is_on = verification.get("ison", False)
                    command_succeeded = device_is_on == command_state
                    
                    if command_succeeded:
                        logger.info(f"Shelly Gen2 command successful: device is now {'on' if device_is_on else 'off'}")
                    else:
                        logger.warning(f"Shelly Gen2 command failed: expected {command_state}, got {device_is_on}")
                    
                    return command_succeeded
                else:
                    logger.warning(f"Shelly Gen2 command sent but couldn't verify state")
                    return False
                    
        else:
            # Gen1 legacy API: /relay/0?turn=on/off
            turn_action = "on" if command_state else "off"
            url = f"http://{device_ip}/relay/0?turn={turn_action}"
            logger.info(f"Sending Shelly Gen1 command to {device_ip}: turn={turn_action}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                
                # Parse the JSON response
                result = response.json()
                logger.debug(f"Shelly Gen1 response: {result}")
                
                # Check if the device's new state matches what we commanded
                device_is_on = result.get("ison", False)
                command_succeeded = device_is_on == command_state
                
                if command_succeeded:
                    logger.info(f"Shelly Gen1 command successful: device is now {'on' if device_is_on else 'off'}")
                else:
                    logger.warning(f"Shelly Gen1 command failed: expected {command_state}, got {device_is_on}")
                
                return command_succeeded
            
    except httpx.RequestError as e:
        logger.error(f"Network error communicating with Shelly device at {device_ip}: {e}")
        return False
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Shelly device at {device_ip}: {e.response.status_code}")
        return False
    except (KeyError, ValueError) as e:
        logger.error(f"Invalid response from Shelly device at {device_ip}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error communicating with Shelly device at {device_ip}: {e}")
        return False


async def send_zwave_command(node_id: int, command_payload: Dict[str, Any]) -> bool:
    """
    Send a command to a Z-Wave device.
    
    Args:
        node_id: Z-Wave node ID of the device
        command_payload: Dictionary containing the command to send
    
    Returns:
        bool: True if command was successful, False otherwise
        
    Note:
        This is a placeholder implementation. In a real system, this would
        interface with a Z-Wave controller like Z-Wave JS or OpenZWave.
    """
    try:
        logger.info(f"Mock Z-Wave command to node {node_id}: {command_payload}")
        
        # Mock implementation - always returns True for testing
        # In a real implementation, this would:
        # 1. Connect to Z-Wave controller
        # 2. Send the command to the specified node
        # 3. Wait for confirmation
        # 4. Return the actual result
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending Z-Wave command to node {node_id}: {e}")
        return False


async def get_device_status(device_type: str, device_ip: Optional[str] = None, 
                          node_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Get current status of a device.
    
    Args:
        device_type: Type of device ("wifi", "zwave", or "govee")
        device_ip: IP address for Wi-Fi/Govee devices
        node_id: Node ID for Z-Wave devices
    
    Returns:
        Dictionary with device status or None if failed
    """
    try:
        if device_type == "wifi" and device_ip:
            return await get_shelly_status(device_ip)
        elif device_type == "zwave" and node_id:
            return await get_zwave_status(node_id)
        elif device_type == "govee" and device_ip:
            from app.core.govee import get_govee_status
            return await get_govee_status(device_ip)
        else:
            logger.error(f"Invalid device parameters: type={device_type}, ip={device_ip}, node_id={node_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting device status: {e}")
        return None


async def get_shelly_status(device_ip: str) -> Optional[Dict[str, Any]]:
    """
    Get current status of a Shelly device.
    Supports both Gen1 (/relay/0) and Gen2 (/rpc/Switch.GetStatus) devices.
    
    Args:
        device_ip: IP address of the Shelly device
    
    Returns:
        Dictionary with device status or None if failed
    """
    try:
        # Detect device generation
        device_generation = await _detect_shelly_generation(device_ip)
        
        async with httpx.AsyncClient() as client:
            if device_generation == "gen2":
                # Gen2 RPC API
                url = f"http://{device_ip}/rpc/Switch.GetStatus?id=0"
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Shelly Gen2 status response: {result}")
                
                # Convert Gen2 response format to common format
                return {
                    "ison": result.get("output", False),
                    "power": result.get("apower", 0),  # Active power
                    "energy": result.get("aenergy", {}).get("total", 0),  # Total energy
                    "temperature": result.get("temperature", {}).get("tC", 0),
                    "overtemperature": result.get("temperature", {}).get("overtemperature", False),
                    "generation": "gen2"
                }
            else:
                # Gen1 legacy API
                url = f"http://{device_ip}/relay/0"
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Shelly Gen1 status response: {result}")
                
                return {
                    "ison": result.get("ison", False),
                    "power": result.get("power", 0),
                    "energy": result.get("energy", 0),
                    "temperature": result.get("temperature", 0),
                    "overtemperature": result.get("overtemperature", False),
                    "generation": "gen1"
                }
            
    except Exception as e:
        logger.error(f"Error getting Shelly status from {device_ip}: {e}")
        return None


async def get_zwave_status(node_id: int) -> Optional[Dict[str, Any]]:
    """
    Get current status of a Z-Wave device.
    
    Args:
        node_id: Z-Wave node ID
    
    Returns:
        Dictionary with device status or None if failed
    """
    try:
        logger.info(f"Mock Z-Wave status request for node {node_id}")
        
        # Mock implementation
        return {
            "is_on": False,
            "battery_level": 100,
            "signal_strength": -50
        }
        
    except Exception as e:
        logger.error(f"Error getting Z-Wave status for node {node_id}: {e}")
        return None
