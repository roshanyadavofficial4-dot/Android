import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class DeveloperOptions:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("controller.developer_options.open", self.open_developer_settings)
        
        self.logger.info("Developer Options Controller initialized. Ready to tinker with the forbidden settings, Sir.")

    async def open_developer_settings(self, data: dict = None):
        self.logger.info("Attempting to open Developer Options...")
        if IS_ANDROID:
            try:
                process = await asyncio.create_subprocess_shell(
                    "am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                self.logger.debug("Developer Options opened.")
                await self.event_bus.publish("speak", {"text": "Developer options opened. Try not to break anything, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to open Developer Options: {e}")
                await self.event_bus.publish("speak", {"text": "It seems Developer Options are not enabled on this device, Sir."})
        else:
            self.logger.warning("Not on Android. Simulating opening Developer Options.")
