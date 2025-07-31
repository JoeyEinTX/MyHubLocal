"""
Device discovery module for Wi-Fi and Z-Wave devices.
This is a simplified version that imports from app.core.discover
"""
from app.core.discover import (
    discover_wifi_devices,
    discover_zwave_devices,
    discover_all_devices,
    merge_discovered_devices
)

# Re-export all discovery functions for backward compatibility
__all__ = [
    'discover_wifi_devices',
    'discover_zwave_devices', 
    'discover_all_devices',
    'merge_discovered_devices'
]
