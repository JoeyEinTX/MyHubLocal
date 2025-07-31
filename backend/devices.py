from fastapi import APIRouter, HTTPException
from typing import List
from models import Device, DeviceAction

router = APIRouter()

# Single test device for development
test_devices = [
    Device(id="plug1", name="Test Plug", status="off", type="zwave")
]

@router.get("/list", response_model=List[Device])
async def list_devices():
    """Get list of all devices"""
    return test_devices

@router.post("/control")
async def control_device(action: DeviceAction):
    """Control a device (turn on/off)"""
    # Find the device
    for device in test_devices:
        if device.id == action.id:
            device.status = action.action
            return {"message": f"Device {action.id} turned {action.action}", "status": "success"}
    
    raise HTTPException(status_code=404, detail="Device not found")
