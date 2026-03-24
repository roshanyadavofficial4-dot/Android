import asyncio
import subprocess
import os
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger

class ScreenshotManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("media.screenshot", self.take_screenshot)
        self.logger.info("Screenshot Manager initialized. Say cheese, Sir.")

    async def take_screenshot(self, data: dict):
        self.logger.info("Taking a screenshot...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"/sdcard/Pictures/Screenshots/ARYA_{timestamp}.png"
        
        try:
            # Requires root on Android to use screencap from Termux
            proc = await asyncio.create_subprocess_exec(
                "su", "-c", f"screencap -p {filepath}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                self.logger.info(f"Screenshot saved to {filepath}")
                await self.event_bus.publish("speak", {"text": "Screenshot captured and saved, Sir."})
            else:
                self.logger.error(f"Screenshot failed: {stderr.decode()}")
                await self.event_bus.publish("speak", {"text": "I failed to take a screenshot, Sir. I may lack the necessary root permissions."})
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
