"""
Device management API endpoints with persistent JSON storage.
Provides endpoints for listing, adding, and controlling smart home devices.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List

# Import our models and registry helper
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models import Device, DeviceAdd, DeviceAction, DeviceResponse
from app.core.registry import (
    load_device_registry,
    save_device_registry, 
    add_device_to_registry,
    update_device_in_registry,
    get_device_from_registry
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/list", response_model=List[Device])
async def list_devices():
    """
    Get the current list of all registered devices.
    Returns a list of Device objects from the persistent registry.
    """
    try:
        devices_data = await load_device_registry()
        
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
async def add_device(device_data: DeviceAdd):
    """
    Add a new device to the registry.
    Accepts device information and saves it to persistent storage.
    """
    try:
        # Check if device already exists
        existing_device = await get_device_from_registry(device_data.id)
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
        success = await add_device_to_registry(new_device.dict())
        
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

@router.post("/control", response_model=DeviceResponse)
async def control_device(action_data: DeviceAction):
    """
    Control a device by toggling its status.
    Updates the device status in persistent storage.
    """
    try:
        # Get the device from registry
        device_data = await get_device_from_registry(action_data.id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{action_data.id}' not found"
            )
        
        # Update device status
        old_status = device_data.get('status', 'off')
        new_status = action_data.action
        
        success = await update_device_in_registry(
            action_data.id, 
            {"status": new_status}
        )
        
        if success:
            # Get updated device data
            updated_device_data = await get_device_from_registry(action_data.id)
            updated_device = Device(**updated_device_data)
            
            logger.info(f"Device {action_data.id} status: {old_status} -> {new_status}")
            return DeviceResponse(
                success=True,
                message=f"Device '{updated_device.name}' turned {new_status}",
                device=updated_device
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update device status"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control device {action_data.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control device: {str(e)}"
        )

@router.get("/status/{device_id}", response_model=Device)
async def get_device_status(device_id: str):
    """
    Get the current status of a specific device.
    Returns detailed device information.
    """
    try:
        device_data = await get_device_from_registry(device_id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        device = Device(**device_data)
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device status for {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device status: {str(e)}"
        )

@router.delete("/remove/{device_id}", response_model=DeviceResponse)
async def remove_device(device_id: str):
    """
    Remove a device from the registry.
    Permanently deletes the device from persistent storage.
    """
    try:
        # Check if device exists
        device_data = await get_device_from_registry(device_id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        # Load all devices and remove the specified one
        all_devices = await load_device_registry()
        updated_devices = [d for d in all_devices if d.get('id') != device_id]
        
        success = await save_device_registry(updated_devices)
        
        if success:
            logger.info(f"Removed device: {device_id}")
            return DeviceResponse(
                success=True,
                message=f"Device '{device_data['name']}' removed successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update device registry"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove device {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove device: {str(e)}"
        )
