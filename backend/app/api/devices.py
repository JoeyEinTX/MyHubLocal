"""
Device management API endpoints with persistent JSON storage.
Provides endpoints for listing, adding, and controlling smart home devices.
"""
import logging
import time
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List

# Import our models and registry helper
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models import Device, DeviceAdd, DeviceAction, DeviceState, DeviceResponse
from app.core.registry import (
    load_device_registry,
    save_device_registry, 
    add_device_to_registry,
    update_device_in_registry,
    get_device_from_registry
)
from app.core.telemetry import telemetry_manager
from app.core.discover import discover_all_devices, merge_discovered_devices
from device_protocols import send_shelly_command, send_zwave_command

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
    Includes comprehensive validation and duplicate prevention.
    """
    try:
        # Input validation and sanitization
        device_id = device_data.id.strip().lower()
        device_name = device_data.name.strip()
        
        # Validate required fields based on device type
        if device_data.type == "wifi" and not device_data.ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IP address is required for Wi-Fi devices"
            )
        elif device_data.type == "zwave" and not device_data.node_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Node ID is required for Z-Wave devices"
            )
        
        # Check if device already exists (by ID or by identifying characteristics)
        existing_device = await get_device_from_registry(device_id)
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device with ID '{device_id}' already exists"
            )
        
        # For Wi-Fi devices, also check if IP is already in use
        if device_data.type == "wifi" and device_data.ip:
            all_devices = await load_device_registry()
            for existing in all_devices:
                if existing.get('ip') == device_data.ip and existing.get('type') == 'wifi':
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"A Wi-Fi device with IP '{device_data.ip}' already exists"
                    )
        
        # Create new device with proper field mapping and validation
        device_fields = {
            "id": device_id,  # Use sanitized ID
            "name": device_name,  # Use sanitized name
            "type": device_data.type,
            "status": "off"  # New devices start as off
        }
        
        # Add type-specific fields
        if device_data.type == "wifi" and device_data.ip:
            device_fields["ip"] = device_data.ip
        elif device_data.type == "zwave" and device_data.node_id:
            device_fields["node_id"] = device_data.node_id
        
        # Add timestamps for better tracking
        from datetime import datetime
        device_fields["added_at"] = datetime.now().isoformat()
        device_fields["last_seen"] = datetime.now().isoformat()
        
        new_device = Device(**device_fields)
        
        # Add to registry
        success = await add_device_to_registry(new_device.dict())
        
        if success:
            logger.info(f"Added new device: {device_data.id} - {device_data.name}")
            
            # Log successful onboarding to telemetry
            await telemetry_manager.log_onboarding_event(
                device_id=device_id,
                device_name=device_name,
                device_type=device_data.type,
                status="added"
            )
            
            return DeviceResponse(
                success=True,
                message=f"Device '{device_data.name}' added successfully",
                device=new_device
            )
        else:
            # Log failed onboarding to telemetry
            await telemetry_manager.log_onboarding_event(
                device_id=device_id,
                device_name=device_name,
                device_type=device_data.type,
                status="failed"
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save device to registry"
            )
            
    except HTTPException:
        # Log failed onboarding for HTTP exceptions (validation errors, conflicts, etc.)
        try:
            await telemetry_manager.log_onboarding_event(
                device_id=getattr(device_data, 'id', 'unknown'),
                device_name=getattr(device_data, 'name', 'unknown'),
                device_type=getattr(device_data, 'type', 'unknown'),
                status="failed"
            )
        except:
            pass  # Don't let telemetry logging errors affect the main flow
        raise
    except Exception as e:
        # Log failed onboarding for other exceptions
        try:
            await telemetry_manager.log_onboarding_event(
                device_id=getattr(device_data, 'id', 'unknown'),
                device_name=getattr(device_data, 'name', 'unknown'),
                device_type=getattr(device_data, 'type', 'unknown'),
                status="failed"
            )
        except:
            pass  # Don't let telemetry logging errors affect the main flow
            
        logger.error(f"Failed to add device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add device: {str(e)}"
        )

@router.put("/{device_id}/state", response_model=DeviceResponse)
async def control_device_state(device_id: str, payload: DeviceState):
    """
    Control a device by sending commands through appropriate protocol handlers.
    Updates the device status via actual device communication.
    """
    try:
        # Get the device from registry
        device_data = await get_device_from_registry(device_id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        device_type = device_data.get('type')
        old_status = device_data.get('status', 'off')
        
        # Send command through appropriate protocol handler
        command_success = False
        
        if device_type == "wifi":
            device_ip = device_data.get('ip')
            if not device_ip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Wi-Fi device '{device_id}' missing IP address"
                )
            command_success = await send_shelly_command(device_ip, payload.state)
            
        elif device_type == "zwave":
            node_id = device_data.get('node_id')
            if not node_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Z-Wave device '{device_id}' missing node ID"
                )
            command_success = await send_zwave_command(node_id, payload.state)
            
        elif device_type == "govee":
            device_ip = device_data.get('ip')
            if not device_ip:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Govee device '{device_id}' missing IP address"
                )
            from app.core.govee import send_govee_command
            
            # Convert state to Govee format
            govee_command = {}
            if "on" in payload.state:
                govee_command["onOff"] = 1 if payload.state["on"] else 0
            if "brightness" in payload.state:
                govee_command["brightness"] = payload.state["brightness"]
            if "color" in payload.state:
                govee_command["color"] = payload.state["color"]
                
            command_success = await send_govee_command(device_ip, govee_command)
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported device type: {device_type}"
            )
        
        # Handle command result
        if command_success:
            # Determine new status from payload
            new_status = "on" if payload.state.get("on", False) else "off"
            
            # Update device status in registry
            success = await update_device_in_registry(
                device_id, 
                {"status": new_status, "last_seen": time.time()}
            )
            
            if success:
                # Get updated device data
                updated_device_data = await get_device_from_registry(device_id)
                updated_device = Device(**updated_device_data)
                
                logger.info(f"Device {device_id} controlled via {device_type}: {old_status} -> {new_status}")
                return DeviceResponse(
                    success=True,
                    message=f"Device '{updated_device.name}' controlled successfully via {device_type} protocol",
                    device=updated_device
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Command succeeded but failed to update device registry"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to control {device_type} device - command was not successful"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control device {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control device: {str(e)}"
        )

@router.get("/status/{device_id}", response_model=Device)
async def get_device_status(device_id: str):
    """
    Get the current status of a specific device.
    Returns detailed device information with last seen timestamp update.
    """
    try:
        device_data = await get_device_from_registry(device_id)
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID '{device_id}' not found"
            )
        
        # Update last_seen timestamp
        from datetime import datetime
        await update_device_in_registry(device_id, {
            "last_seen": datetime.now().isoformat()
        })
        
        # Get updated device data
        updated_device_data = await get_device_from_registry(device_id)
        device = Device(**updated_device_data)
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device status for {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device status: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def get_devices_health():
    """
    Get health status of all devices including connectivity and last seen times.
    Useful for dashboard monitoring and alerting.
    """
    try:
        devices_data = await load_device_registry()
        from datetime import datetime, timedelta
        
        health_info = {
            "total_devices": len(devices_data),
            "online_devices": 0,
            "offline_devices": 0,
            "unknown_devices": 0,
            "devices_by_type": {"wifi": 0, "zwave": 0},
            "stale_devices": []  # Devices not seen in last 24 hours
        }
        
        now = datetime.now()
        stale_threshold = now - timedelta(hours=24)
        
        for device_data in devices_data:
            device_type = device_data.get('type', 'unknown')
            if device_type in health_info["devices_by_type"]:
                health_info["devices_by_type"][device_type] += 1
            
            status = device_data.get('status', 'unknown')
            if status == 'on':
                health_info["online_devices"] += 1
            elif status == 'off':
                health_info["offline_devices"] += 1
            else:
                health_info["unknown_devices"] += 1
            
            # Check if device is stale
            last_seen_str = device_data.get('last_seen')
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    if last_seen < stale_threshold:
                        health_info["stale_devices"].append({
                            "id": device_data.get('id'),
                            "name": device_data.get('name'),
                            "last_seen": last_seen_str
                        })
                except:
                    pass
        
        return health_info
        
    except Exception as e:
        logger.error(f"Failed to get devices health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get devices health: {str(e)}"
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

@router.get("/discover")
async def discover_devices():
    """
    Discover available devices from Wi-Fi (Shelly) and Z-Wave networks.
    
    Returns:
        Dict containing discovered devices and discovery metadata.
        List of discovered devices with their connection details.
    """
    try:
        logger.info("Starting device discovery scan...")
        start_time = time.time()
        
        # Run comprehensive discovery (Wi-Fi + Z-Wave)
        discovery_results = await discover_all_devices()
        
        # Merge and deduplicate discovered devices
        discovered_devices = merge_discovered_devices(discovery_results)
        
        # Create discovery summary
        summary = {
            "discovered_devices": discovered_devices,
            "discovery_summary": {
                "wifi_devices": len(discovery_results.get("wifi", [])),
                "zwave_devices": len(discovery_results.get("zwave", [])),
                "total_discovered": len(discovered_devices),
                "scan_duration": round(time.time() - start_time, 2)
            },
            "scan_timestamp": time.time()
        }
        
        # Log discovery scan to telemetry
        try:
            await telemetry_manager.log_discovery_event(
                wifi_found=summary["discovery_summary"]["wifi_devices"],
                zwave_found=summary["discovery_summary"]["zwave_devices"],
                duration_ms=int(summary["discovery_summary"]["scan_duration"] * 1000)
            )
            logger.info(f"Discovery scan completed. Found {len(discovered_devices)} devices in {summary['discovery_summary']['scan_duration']}s")
        except Exception as e:
            logger.warning(f"Failed to log discovery event to telemetry: {e}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Discovery scan failed: {e}")
        
        # Log failed discovery to telemetry
        try:
            await telemetry_manager.log_discovery_event(
                wifi_found=0,
                zwave_found=0,
                duration_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as log_error:
            logger.warning(f"Failed to log discovery error to telemetry: {log_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discovery scan failed: {str(e)}"
        )
