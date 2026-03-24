import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID

class AppCloser:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("app.close.background", self.close_background_apps)
        self.logger.info("App Closer initialized. I will terminate unnecessary processes with extreme prejudice, Sir.")

    async def close_background_apps(self, data: dict):
        self.logger.info("Initiating background app purge...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            if device:
                try:
                    # uiautomator2 has app_clear to stop an app and clear its data, 
                    # but to just stop background apps, we can use app_stop_all
                    await asyncio.to_thread(device.app_stop_all)
                    self.logger.info("Successfully terminated all background applications.")
                    await self.event_bus.publish("speak", {"text": "Background applications terminated. Memory freed, Sir."})
                except Exception as e:
                    self.logger.error(f"Failed to close background apps: {e}")
            else:
                self.logger.warning("Device not connected. Cannot close background apps.")
        else:
            self.logger.info("Background app purge is not natively supported on PC via this module.")
            await self.event_bus.publish("speak", {"text": "I cannot purge background apps on your PC, Sir. You'll have to use Task Manager."})
