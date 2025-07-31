"""
Device management API endpoints with persistent JSON storage.
This file provides backward compatibility and should redirect to app.api.devices
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from models import Device, DeviceAdd, DeviceAction, DeviceResponse
from app.core.registry import (
    load_registry,
    save_registry,
    add_device,
    remove_device,
    get_device,
    update_device_status
)
from app.core.discover import discover_all_devices, merge_discovered_devices

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/list", response_model=List[Device])
async def list_devices():
    """Get list of all devices from persistent storage"""
    try:
        devices_data = await load_registry()
        
        # Convert raw dict data to Device models for validation
        devices = []
        for device_data in devices_data:
            try:
                device = Device(**device_data)
                devices.append(device)
            except Exception as e:
                logger.warning(f"Skipping invalid device data {device_data}: {e}")
                continue
                
        logger.info(f"Returning {len(devices)} devices")
        return devices
        
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load device registry"
        )

@router.post("/add", response_model=DeviceResponse)
async def add_device_endpoint(device_data: DeviceAdd):
    """Add a new device to the registry"""
    try:
        # Check if device already exists
        existing_device = await get_device(device_data.id)
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device with ID '{device_data.id}' already exists"
            )
        
        # Create new device with default status "off"
        new_device = Device(
            id=device_data.id,
            name=device_data.name,
            ip=device_data.ip,
            type=device_data.type,
            status="off"  # New devices start as off
        )
        
        # Add to registry
        success = await add_device(new_device.dict())
        
        if success:
            logger.info(f"Added new device: {device_data.id} - {device_data.name}")
            return DeviceResponse(
                success=True,
                message=f"Device '{device_data.name}' added successfully",
                device=new_device
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save device to registry"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add device: {str(e)}"
        )

@router.post("/control")
async def control_device(action: DeviceAction):
    """Control a device (turn on/off)"""
    try:
        # Get the device from registry
        device_data = await get_device(action.id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{action.id}' not found"
            )
        
        # Update device status
        old_status = device_data.get('status', 'off')
        new_status = action.action
        
        success = await update_device_status(
            action.id, 
            new_status
        )
        
        if success:
            logger.info(f"Device {action.id} status: {old_status} -> {new_status}")
            return {
                "message": f"Device {action.id} turned {new_status}", 
                "status": "success"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update device status"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control device {action.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control device: {str(e)}"
        )

@router.delete("/remove/{device_id}", response_model=DeviceResponse)
async def remove_device_endpoint(device_id: str):
    """Remove a device from the registry"""
    try:
        # Check if device exists
        device_data = await get_device(device_id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        # Remove device from registry
        success = await remove_device(device_id)
        
        if success:
            logger.info(f"Removed device: {device_id}")
            return DeviceResponse(
                success=True,
                message=f"Device '{device_data['name']}' removed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove device from registry"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove device {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove device: {str(e)}"
        )

@router.get("/discover")
async def discover_devices():
    """
    Discover available devices from Wi-Fi (Shelly) and Z-Wave networks.
    Scans for devices that can be added to the registry.
    This is a read-only operation - no devices are automatically added.
    
    Returns:
        List of discovered devices with their connection details.
    """
    try:
        logger.info("Starting device discovery scan...")
        
        # Run comprehensive discovery (Wi-Fi + Z-Wave)
        discovery_results = await discover_all_devices()
        
        # Merge results into a single list
        discovered_devices = merge_discovered_devices(discovery_results)
        
        # Add discovery metadata
        response = {
            "discovered_devices": discovered_devices,
            "discovery_summary": {
                "wifi_devices": len(discovery_results.get("wifi", [])),
                "zwave_devices": len(discovery_results.get("zwave", [])),
                "total_discovered": len(discovered_devices)
            },
            "discovery_methods": {
                "wifi": "zeroconf scan for Shelly devices",
                "zwave": "Z-Wave controller scan (mock for development)"
            }
        }
        
        logger.info(f"Discovery completed: {len(discovered_devices)} devices found")
        return response
        
    except Exception as e:
        logger.error(f"Device discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Device discovery failed: {str(e)}"
        )

@router.get("/discover/wifi")
async def discover_wifi_only():
    """
    Discover only Wi-Fi devices (Shelly plugs and switches).
    Useful for testing Wi-Fi discovery in isolation.
    """
    try:
        from app.core.discover import discover_wifi_devices
        
        logger.info("Starting Wi-Fi-only device discovery...")
        wifi_devices = await discover_wifi_devices()
        
        return {
            "wifi_devices": wifi_devices,
            "count": len(wifi_devices),
            "discovery_method": "zeroconf scan for _http._tcp.local."
        }
        
    except Exception as e:
        logger.error(f"Wi-Fi discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wi-Fi discovery failed: {str(e)}"
        )

@router.get("/discover/zwave")
async def discover_zwave_only():
    """
    Discover only Z-Wave devices from the connected controller.
    Useful for testing Z-Wave discovery in isolation.
    """
    try:
        from app.core.discover import discover_zwave_devices
        
        logger.info("Starting Z-Wave-only device discovery...")
        zwave_devices = await discover_zwave_devices()
        
        return {
            "zwave_devices": zwave_devices,
            "count": len(zwave_devices),
            "discovery_method": "Z-Wave controller scan"
        }
        
    except Exception as e:
        logger.error(f"Z-Wave discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Z-Wave discovery failed: {str(e)}"
        )

@router.get("/{device_id}", response_model=Device)
async def get_device_by_id(device_id: str):
    """Get a specific device by ID from persistent storage"""
    try:
        device_data = await get_device(device_id)
        if device_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        device = Device(**device_data)
        logger.info(f"Retrieved device: {device_id}")
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve device"
        )
