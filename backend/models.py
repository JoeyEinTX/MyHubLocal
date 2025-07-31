from pydantic import BaseModel
from typing import Literal

class Device(BaseModel):
    id: str
    name: str
    status: Literal["on", "off"]
    type: str = "zwave"  # Default to zwave for now

class DeviceAction(BaseModel):
    id: str
    action: Literal["on", "off"]
