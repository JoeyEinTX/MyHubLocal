"""
Telemetry logging system for device discovery and onboarding events.
Provides persistent storage and retrieval of scan history and device addition events.
"""
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import shutil
import os

logger = logging.getLogger(__name__)

class TelemetryManager:
    """
    Manages telemetry data persistence with atomic writes and backup support.
    Tracks discovery scans and device onboarding events for analytics and troubleshooting.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.telemetry_file = self.data_dir / "telemetry.json"
        self.backup_file = self.data_dir / "telemetry.json.backup"
        
        # Initialize telemetry file if it doesn't exist
        self._ensure_telemetry_file()
    
    def _ensure_telemetry_file(self):
        """Initialize telemetry file with empty structure if it doesn't exist."""
        if not self.telemetry_file.exists():
            initial_data = {
                "discovery_history": [],
                "onboarding_history": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self._write_telemetry_data(initial_data)
    
    async def _read_telemetry_data(self) -> Dict[str, Any]:
        """
        Safely read telemetry data from file.
        Falls back to backup if main file is corrupted.
        """
        try:
            if self.telemetry_file.exists():
                with open(self.telemetry_file, 'r') as f:
                    data = json.load(f)
                    # Validate structure
                    if "discovery_history" in data and "onboarding_history" in data:
                        return data
                    else:
                        logger.warning("Invalid telemetry file structure, attempting backup recovery")
                        
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read telemetry file: {e}")
        
        # Try backup file
        try:
            if self.backup_file.exists():
                logger.info("Attempting to restore from backup telemetry file")
                with open(self.backup_file, 'r') as f:
                    data = json.load(f)
                    # Restore main file from backup
                    self._write_telemetry_data(data)
                    return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read backup telemetry file: {e}")
        
        # If both fail, return empty structure
        logger.warning("Creating new telemetry file due to corruption")
        return {
            "discovery_history": [],
            "onboarding_history": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def _write_telemetry_data(self, data: Dict[str, Any]):
        """
        Atomically write telemetry data with backup support.
        Uses temporary file and atomic move to prevent corruption.
        """
        try:
            # Create backup of current file
            if self.telemetry_file.exists():
                shutil.copy2(self.telemetry_file, self.backup_file)
            
            # Write to temporary file first
            temp_file = self.telemetry_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic move
            shutil.move(str(temp_file), str(self.telemetry_file))
            logger.debug("Successfully wrote telemetry data")
            
        except Exception as e:
            logger.error(f"Failed to write telemetry data: {e}")
            # Clean up temp file if it exists
            temp_file = self.telemetry_file.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    async def log_discovery_event(self, 
                                wifi_found: int, 
                                zwave_found: int, 
                                duration_ms: int) -> bool:
        """
        Log a device discovery scan event.
        
        Args:
            wifi_found: Number of Wi-Fi devices discovered
            zwave_found: Number of Z-Wave devices discovered
            duration_ms: Duration of scan in milliseconds
            
        Returns:
            bool: True if logged successfully
        """
        try:
            data = await self._read_telemetry_data()
            
            discovery_event = {
                "timestamp": datetime.now().isoformat(),
                "wifi_found": wifi_found,
                "zwave_found": zwave_found,
                "total_found": wifi_found + zwave_found,
                "duration_ms": duration_ms
            }
            
            # Add to history (keep last 50 events)
            data["discovery_history"].append(discovery_event)
            data["discovery_history"] = data["discovery_history"][-50:]
            
            self._write_telemetry_data(data)
            logger.info(f"Logged discovery event: {wifi_found} Wi-Fi, {zwave_found} Z-Wave devices found")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log discovery event: {e}")
            return False
    
    async def log_onboarding_event(self, 
                                 device_id: str, 
                                 device_name: str, 
                                 device_type: str, 
                                 status: str) -> bool:
        """
        Log a device onboarding event.
        
        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_type: Type of device (wifi or zwave)
            status: Status of onboarding (added or failed)
            
        Returns:
            bool: True if logged successfully
        """
        try:
            data = await self._read_telemetry_data()
            
            onboarding_event = {
                "timestamp": datetime.now().isoformat(),
                "device_id": device_id,
                "device_name": device_name,
                "type": device_type,
                "status": status
            }
            
            # Add to history (keep last 100 events)
            data["onboarding_history"].append(onboarding_event)
            data["onboarding_history"] = data["onboarding_history"][-100:]
            
            self._write_telemetry_data(data)
            logger.info(f"Logged onboarding event: {device_name} ({device_type}) - {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log onboarding event: {e}")
            return False
    
    async def get_discovery_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent discovery history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of discovery events, newest first
        """
        try:
            data = await self._read_telemetry_data()
            history = data.get("discovery_history", [])
            
            # Return newest first
            return list(reversed(history[-limit:]))
            
        except Exception as e:
            logger.error(f"Failed to get discovery history: {e}")
            return []
    
    async def get_onboarding_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent onboarding history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of onboarding events, newest first
        """
        try:
            data = await self._read_telemetry_data()
            history = data.get("onboarding_history", [])
            
            # Return newest first
            return list(reversed(history[-limit:]))
            
        except Exception as e:
            logger.error(f"Failed to get onboarding history: {e}")
            return []
    
    async def get_last_scan_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary of the most recent discovery scan.
        
        Returns:
            Dict with last scan info or None if no scans found
        """
        try:
            discovery_history = await self.get_discovery_history(limit=1)
            if discovery_history:
                last_scan = discovery_history[0]
                
                # Get successful onboarding count since this scan
                onboarding_history = await self.get_onboarding_history(limit=20)
                scan_time = datetime.fromisoformat(last_scan["timestamp"])
                
                added_count = 0
                for event in onboarding_history:
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if event_time >= scan_time and event["status"] == "added":
                        added_count += 1
                
                return {
                    **last_scan,
                    "devices_added": added_count
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last scan summary: {e}")
            return None

# Global telemetry manager instance
telemetry_manager = TelemetryManager()
