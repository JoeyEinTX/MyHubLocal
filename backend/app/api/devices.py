from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Basic data model for controlling a device
class DeviceAction(BaseModel):
    device_id: str
    action: str  # "on" or "off"

# Example static device list (later will use ZwaveManager)
devices = [
    {"id": "plug1", "name": "Living Room Plug", "status": "off"},
    {"id": "plug2", "name": "Bedroom Plug", "status": "on"}
]

@router.get("/list")
async def list_devices():
    return devices

@router.post("/control")
async def control_device(data: DeviceAction):
    # Find the device in our list
    for device in devices:
        if device["id"] == data.device_id:
            device["status"] = data.action
            return {"message": f"Device {data.device_id} turned {data.action}"}
    return {"error": "Device not found"}
