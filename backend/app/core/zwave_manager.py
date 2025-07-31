class ZwaveManager:
    """
    Handles Z-Wave device discovery and control.
    Placeholder implementation for now.
    """

    def __init__(self):
        # Later, this will initialize the Z-Wave USB stick, etc.
        self.devices = {
            "plug1": {"name": "Living Room Plug", "status": "off"},
            "plug2": {"name": "Bedroom Plug", "status": "on"}
        }

    def list_devices(self):
        return [{"id": k, "name": v["name"], "status": v["status"]} for k, v in self.devices.items()]

    def control_device(self, device_id, action):
        if device_id in self.devices:
            self.devices[device_id]["status"] = action
            return True
        return False
