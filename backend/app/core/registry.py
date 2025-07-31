"""
Device registry management for persistent storage.
Handles loading and saving devices to/from devices_registry.json.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

# Registry file path - moved to data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
REGISTRY_FILE = DATA_DIR / "devices_registry.json"

def async_file_operation(func):
    """Decorator to run file operations in thread pool"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper

@async_file_operation
def _load_registry_sync() -> List[Dict[str, Any]]:
    """Synchronous function to load registry from file"""
    try:
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        if not REGISTRY_FILE.exists():
            logger.info(f"Registry file {REGISTRY_FILE} not found. Creating with sample devices.")
            # Create sample devices for initial setup
            sample_devices = [
                {
                    "id": "living_room_light",
                    "name": "Living Room Light",
                    "type": "wifi",
                    "ip": "192.168.1.100",
                    "status": "unknown",
                    "added_at": datetime.now().isoformat(),
                    "last_seen": None
                },
                {
                    "id": "kitchen_switch",
                    "name": "Kitchen Switch",
                    "type": "zwave",
                    "node_id": 2,
                    "status": "unknown",
                    "added_at": datetime.now().isoformat(),
                    "last_seen": None
                }
            ]
            _save_registry_sync(sample_devices)
            return sample_devices
            
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                logger.warning("Registry file is empty. Initializing with empty list.")
                return []
                
            devices = json.loads(content)
            if not isinstance(devices, list):
                logger.error("Registry file contains invalid format. Expected list.")
                return []
                
            logger.info(f"Loaded {len(devices)} devices from registry")
            return devices
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse registry file: {e}")
        # Backup corrupted file
        backup_path = REGISTRY_FILE.with_suffix('.json.backup')
        if REGISTRY_FILE.exists():
            REGISTRY_FILE.rename(backup_path)
            logger.info(f"Corrupted registry backed up to {backup_path}")
        return []
        
    except Exception as e:
        logger.error(f"Unexpected error loading registry: {e}")
        return []

@async_file_operation
def _save_registry_sync(devices: List[Dict[str, Any]]) -> bool:
    """Synchronous function to save registry to file"""
    try:
        # Ensure directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file first, then rename (atomic operation)
        temp_file = REGISTRY_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(devices, f, indent=2, ensure_ascii=False)
            
        # Atomic rename
        temp_file.rename(REGISTRY_FILE)
        logger.info(f"Saved {len(devices)} devices to registry")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save registry: {e}")
        # Clean up temp file if it exists
        temp_file = REGISTRY_FILE.with_suffix('.tmp')
        if temp_file.exists():
            temp_file.unlink()
        return False

# Main registry functions
async def load_registry() -> List[Dict[str, Any]]:
    """
    Load all devices from the registry file.
    Creates file with sample devices if it doesn't exist.
    Returns empty list if file is corrupted.
    """
    return await _load_registry_sync()

async def save_registry(devices: List[Dict[str, Any]]) -> bool:
    """
    Save devices to the registry file.
    Returns True if successful, False otherwise.
    """
    return await _save_registry_sync(devices)

async def get_devices() -> List[Dict[str, Any]]:
    """
    Get all devices from registry.
    Alias for load_registry for better API naming.
    """
    return await load_registry()

async def add_device(device_data: Dict[str, Any]) -> bool:
    """
    Add a new device to the registry.
    Validates device data and handles duplicates.
    
    Args:
        device_data: Device information dictionary
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        devices = await load_registry()
        
        # Validate required fields
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in device_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check if device ID already exists
        existing_device = next((d for d in devices if d.get('id') == device_data.get('id')), None)
        if existing_device:
            logger.warning(f"Device with ID {device_data.get('id')} already exists. Updating instead.")
            # Update existing device
            existing_device.update(device_data)
            existing_device['updated_at'] = datetime.now().isoformat()
        else:
            # Add timestamps
            device_data['added_at'] = datetime.now().isoformat()
            device_data['last_seen'] = None
            
            # Set default status if not provided
            if 'status' not in device_data:
                device_data['status'] = 'unknown'
            
            devices.append(device_data)
            
        return await save_registry(devices)
        
    except Exception as e:
        logger.error(f"Failed to add device to registry: {e}")
        return False

async def remove_device(device_id: str) -> bool:
    """
    Remove a device from the registry by ID.
    
    Args:
        device_id: ID of the device to remove
        
    Returns:
        True if successful, False if device not found or error.
    """
    try:
        devices = await load_registry()
        
        # Find and remove device
        original_count = len(devices)
        devices = [d for d in devices if d.get('id') != device_id]
        
        if len(devices) == original_count:
            logger.warning(f"Device with ID {device_id} not found for removal")
            return False
            
        success = await save_registry(devices)
        if success:
            logger.info(f"Removed device: {device_id}")
        return success
        
    except Exception as e:
        logger.error(f"Failed to remove device from registry: {e}")
        return False

async def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific device from the registry by ID.
    
    Args:
        device_id: ID of the device to retrieve
        
    Returns:
        Device dict if found, None otherwise.
    """
    try:
        devices = await load_registry()
        
        device = next((d for d in devices if d.get('id') == device_id), None)
        return device
        
    except Exception as e:
        logger.error(f"Failed to get device from registry: {e}")
        return None

async def update_device_status(device_id: str, status: str) -> bool:
    """
    Update the status of a device in the registry.
    
    Args:
        device_id: ID of the device to update
        status: New status value
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        devices = await load_registry()
        
        device = next((d for d in devices if d.get('id') == device_id), None)
        if not device:
            logger.warning(f"Device with ID {device_id} not found for status update")
            return False
            
        device['status'] = status
        device['last_seen'] = datetime.now().isoformat()
        
        return await save_registry(devices)
        
    except Exception as e:
        logger.error(f"Failed to update device status: {e}")
        return False

# Legacy compatibility functions
async def load_device_registry() -> List[Dict[str, Any]]:
    """Legacy compatibility function"""
    return await load_registry()

async def save_device_registry(devices: List[Dict[str, Any]]) -> bool:
    """Legacy compatibility function"""
    return await save_registry(devices)

async def add_device_to_registry(device: Dict[str, Any]) -> bool:
    """Legacy compatibility function"""
    return await add_device(device)

async def update_device_in_registry(device_id: str, updates: Dict[str, Any]) -> bool:
    """Legacy compatibility function"""
    device = await get_device(device_id)
    if not device:
        return False
    
    device.update(updates)
    device['updated_at'] = datetime.now().isoformat()
    
    devices = await load_registry()
    return await save_registry(devices)

async def get_device_from_registry(device_id: str) -> Dict[str, Any] | None:
    """Legacy compatibility function"""
    return await get_device(device_id)
