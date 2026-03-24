import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None

class AccessibilityDriver:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.device = None
        self.logger.info("Accessibility Driver initializing. Preparing to hijack the UI, Sir.")
        self._connect()

    def _connect(self):
        if not u2:
            self.logger.warning("uiautomator2 not installed. UI automation will be simulated. How quaint.")
            return
        try:
            # Connect to local device (requires ADB enabled and uiautomator2 server running on device)
            self.device = u2.connect()
            device_info = self.device.info.get('model', 'Unknown Device')
            self.logger.info(f"Successfully connected to Android UI Automator on: {device_info}")
        except Exception as e:
            self.logger.error(f"Failed to connect to uiautomator2 server: {e}")
            self.logger.error("Please ensure ADB is enabled and the uiautomator2 server is running.")

    def get_device(self):
        return self.device
