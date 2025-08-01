from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Union, Dict, Any
import re
from datetime import datetime

class Device(BaseModel):
    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable device name")
    status: Literal["on", "off", "unknown"] = Field(default="unknown", description="Current device status")
    type: Literal["wifi", "zwave"] = Field(..., description="Device connection type")
    ip: Optional[str] = Field(None, description="Device IP address (for Wi-Fi devices)")
    node_id: Optional[int] = Field(None, description="Z-Wave node ID (for Z-Wave devices)")
    added_at: Optional[str] = Field(None, description="Timestamp when device was added")
    last_seen: Optional[str] = Field(None, description="Timestamp when device was last seen")
    
    @validator('id')
    def validate_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Device ID must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @validator('ip')
    def validate_ip(cls, v):
        if v is None:
            return v
        # Basic IP validation
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', v):
            raise ValueError('Invalid IP address format')
        return v

    @validator('node_id')
    def validate_node_id(cls, v):
        if v is not None and (v < 1 or v > 232):
            raise ValueError('Z-Wave node ID must be between 1 and 232')
        return v

class DeviceAdd(BaseModel):
    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable device name")
    type: Literal["wifi", "zwave"] = Field(..., description="Device connection type")
    ip: Optional[str] = Field(None, description="Device IP address (required for Wi-Fi devices)")
    node_id: Optional[int] = Field(None, description="Z-Wave node ID (required for Z-Wave devices)")
    
    @validator('id')
    def validate_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Device ID must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @validator('ip')
    def validate_ip(cls, v):
        if v is None:
            return v
        # Basic IP validation
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', v):
            raise ValueError('Invalid IP address format')
        return v

    @validator('node_id')
    def validate_node_id(cls, v):
        if v is not None and (v < 1 or v > 232):
            raise ValueError('Z-Wave node ID must be between 1 and 232')
        return v

    @validator('ip', always=True)
    def validate_wifi_device(cls, v, values):
        device_type = values.get('type')
        if device_type == 'wifi' and not v:
            raise ValueError('IP address is required for Wi-Fi devices')
        return v

    @validator('node_id', always=True)  
    def validate_zwave_device(cls, v, values):
        device_type = values.get('type')
        if device_type == 'zwave' and not v:
            raise ValueError('Node ID is required for Z-Wave devices')
        return v

class DeviceAction(BaseModel):
    id: str = Field(..., description="Device ID to control")
    action: Literal["on", "off"] = Field(..., description="Action to perform")

class DeviceState(BaseModel):
    state: Dict[str, Any] = Field(..., description="Flexible state dictionary for device control")

class DeviceResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    device: Optional[Device] = Field(None, description="Device data if applicable")
