"""
Scenes management API endpoints.
Provides endpoints for listing and activating predefined scenes.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

# Import our models and existing device functionality
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from models import DeviceAction, DeviceResponse
from app.core.registry import load_device_registry
from app.api.devices import control_device

logger = logging.getLogger(__name__)
router = APIRouter()

# Scene models
class Scene(BaseModel):
    id: str
    name: str
    description: str

class SceneActivate(BaseModel):
    scene_id: str

class SceneResponse(BaseModel):
    success: bool
    message: str
    affected_devices: int = 0

# Static scene definitions
SCENES = [
    Scene(
        id="scene_all_on",
        name="All Devices On",
        description="Turn all devices ON immediately"
    ),
    Scene(
        id="scene_all_off", 
        name="All Devices Off",
        description="Turn all devices OFF immediately"
    ),
    Scene(
        id="scene_dusk_to_sunrise",
        name="Dusk to Sunrise",
        description="Schedule lights ON at dusk, OFF at sunrise"
    ),
    Scene(
        id="scene_sunset_to_11pm",
        name="Sunset to 11 PM", 
        description="Schedule lights ON 30 min before sunset, OFF at 11 PM"
    )
]

@router.get("/list", response_model=List[Scene])
async def list_scenes():
    """
    Get the list of available scenes.
    Returns static scene definitions.
    """
    logger.info(f"Returning {len(SCENES)} available scenes")
    return SCENES

@router.post("/activate", response_model=SceneResponse)
async def activate_scene(scene_data: SceneActivate):
    """
    Activate a scene by its ID.
    Handles immediate actions and mock scheduling for complex scenes.
    """
    try:
        # Validate scene exists
        scene = next((s for s in SCENES if s.id == scene_data.scene_id), None)
        if not scene:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scene '{scene_data.scene_id}' not found"
            )
        
        logger.info(f"Activating scene: {scene.name}")
        
        # Handle different scene types
        if scene_data.scene_id == "scene_all_on":
            return await activate_all_devices("on")
        elif scene_data.scene_id == "scene_all_off":
            return await activate_all_devices("off")
        elif scene_data.scene_id in ["scene_dusk_to_sunrise", "scene_sunset_to_11pm"]:
            # Mock scheduling for now
            logger.info(f"Mock scheduling activated for {scene.name}")
            return SceneResponse(
                success=True,
                message=f"Scene '{scene.name}' scheduled successfully",
                affected_devices=0
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scene activation not implemented for '{scene_data.scene_id}'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate scene {scene_data.scene_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate scene: {str(e)}"
        )

async def activate_all_devices(action: str) -> SceneResponse:
    """
    Helper function to turn all devices on or off.
    """
    try:
        # Get all devices
        devices_data = await load_device_registry()
        
        if not devices_data:
            return SceneResponse(
                success=True,
                message=f"No devices available to turn {action}",
                affected_devices=0
            )
        
        successful_controls = 0
        failed_controls = 0
        
        # Control each device
        for device_data in devices_data:
            try:
                device_action = DeviceAction(id=device_data.get('id'), action=action)
                result = await control_device(device_action)
                if result.success:
                    successful_controls += 1
                else:
                    failed_controls += 1
                    logger.warning(f"Failed to control device {device_data.get('id')}: {result.message}")
            except Exception as e:
                failed_controls += 1
                logger.warning(f"Error controlling device {device_data.get('id')}: {e}")
        
        total_devices = len(devices_data)
        
        if failed_controls == 0:
            message = f"Successfully turned {action} {successful_controls} device(s)"
        elif successful_controls == 0:
            message = f"Failed to turn {action} any devices"
        else:
            message = f"Turned {action} {successful_controls} of {total_devices} device(s), {failed_controls} failed"
        
        return SceneResponse(
            success=successful_controls > 0,
            message=message,
            affected_devices=successful_controls
        )
        
    except Exception as e:
        logger.error(f"Error in activate_all_devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control devices: {str(e)}"
        )
