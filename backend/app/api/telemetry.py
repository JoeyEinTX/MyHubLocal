"""
Telemetry API endpoints for tracking device discovery and onboarding events.
Provides endpoints for logging and retrieving telemetry data.
"""
import logging
import time
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.telemetry import telemetry_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class DiscoveryLogRequest(BaseModel):
    wifi_found: int
    zwave_found: int
    duration_ms: int

class OnboardingLogRequest(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    status: str  # "added" or "failed"

class TelemetryResponse(BaseModel):
    success: bool
    message: str

@router.get("/discovery-history")
async def get_discovery_history(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent device discovery scan history.
    
    Args:
        limit: Maximum number of events to return (default 10)
        
    Returns:
        Dictionary containing discovery history events
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 50"
            )
        
        history = await telemetry_manager.get_discovery_history(limit=limit)
        
        return {
            "success": True,
            "count": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get discovery history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve discovery history"
        )

@router.get("/onboarding-history")
async def get_onboarding_history(limit: int = 10) -> Dict[str, Any]:
    """
    Get recent device onboarding event history.
    
    Args:
        limit: Maximum number of events to return (default 10)
        
    Returns:
        Dictionary containing onboarding history events
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 50"
            )
        
        history = await telemetry_manager.get_onboarding_history(limit=limit)
        
        return {
            "success": True,
            "count": len(history),
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get onboarding history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding history"
        )

@router.get("/scan-summary")
async def get_last_scan_summary() -> Dict[str, Any]:
    """
    Get summary of the most recent discovery scan including success metrics.
    
    Returns:
        Dictionary containing last scan summary or null if no scans found
    """
    try:
        summary = await telemetry_manager.get_last_scan_summary()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get scan summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan summary"
        )

@router.post("/log-discovery", response_model=TelemetryResponse)
async def log_discovery_event(request: DiscoveryLogRequest):
    """
    Log a device discovery scan event.
    This endpoint is called internally after discovery operations.
    
    Args:
        request: Discovery event data
        
    Returns:
        Success response
    """
    try:
        success = await telemetry_manager.log_discovery_event(
            wifi_found=request.wifi_found,
            zwave_found=request.zwave_found,
            duration_ms=request.duration_ms
        )
        
        if success:
            return TelemetryResponse(
                success=True,
                message=f"Discovery event logged: {request.wifi_found + request.zwave_found} devices found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log discovery event"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log discovery event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log discovery event: {str(e)}"
        )

@router.post("/log-onboarding", response_model=TelemetryResponse)
async def log_onboarding_event(request: OnboardingLogRequest):
    """
    Log a device onboarding event.
    This endpoint is called internally after device addition attempts.
    
    Args:
        request: Onboarding event data
        
    Returns:
        Success response
    """
    try:
        # Validate status
        if request.status not in ["added", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be either 'added' or 'failed'"
            )
        
        success = await telemetry_manager.log_onboarding_event(
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            status=request.status
        )
        
        if success:
            return TelemetryResponse(
                success=True,
                message=f"Onboarding event logged: {request.device_name} - {request.status}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log onboarding event"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to log onboarding event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log onboarding event: {str(e)}"
        )
