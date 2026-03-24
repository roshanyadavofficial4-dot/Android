import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class WifiController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("controller.wifi.on", self.turn_on)
        self.event_bus.subscribe("controller.wifi.off", self.turn_off)
        
        self.logger.info("WiFi Controller initialized. Managing your connection to the outside world.")

    async def turn_on(self, data: dict = None):
        self.logger.info("Enabling WiFi...")
        if IS_ANDROID:
            try:
                process = await asyncio.create_subprocess_exec(
                    "termux-wifi-enable", "true",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                self.logger.debug("WiFi enabled. We are online, Sir.")
            except Exception as e:
                self.logger.error(f"Failed to enable WiFi: {e}")
                await self.event_bus.publish("speak", {"text": "I lack the permissions to toggle WiFi directly on this Android version, Sir."})
        else:
            self.logger.warning("Not on Android. Simulating WiFi ON.")

    async def turn_off(self, data: dict = None):
        self.logger.info("Disabling WiFi...")
        if IS_ANDROID:
            try:
                process = await asyncio.create_subprocess_exec(
                    "termux-wifi-enable", "false",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                self.logger.debug("WiFi disabled. Going dark, Sir.")
            except Exception as e:
                self.logger.error(f"Failed to disable WiFi: {e}")
        else:
            self.logger.warning("Not on Android. Simulating WiFi OFF.")
