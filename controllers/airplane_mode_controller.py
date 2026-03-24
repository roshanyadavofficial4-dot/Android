import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class AirplaneModeController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("controller.airplane_mode.on", self.turn_on)
        self.event_bus.subscribe("controller.airplane_mode.off", self.turn_off)
        
        self.logger.info("Airplane Mode Controller initialized. Ready for takeoff, Sir.")

    async def turn_on(self, data: dict = None):
        self.logger.info("Enabling Airplane Mode...")
        if IS_ANDROID:
            try:
                # Requires root
                process = await asyncio.create_subprocess_shell(
                    "su -c 'settings put global airplane_mode_on 1 && am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                if process.returncode != 0:
                    self.logger.warning("Root method failed. Opening settings.")
                    await asyncio.create_subprocess_shell("am start -a android.settings.AIRPLANE_MODE_SETTINGS")
                    await self.event_bus.publish("speak", {"text": "I cannot toggle Airplane Mode directly without root, Sir. I have opened the settings for you."})
                else:
                    self.logger.debug("Airplane Mode enabled.")
            except Exception as e:
                self.logger.error(f"Failed to enable Airplane Mode: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Airplane Mode ON.")

    async def turn_off(self, data: dict = None):
        self.logger.info("Disabling Airplane Mode...")
        if IS_ANDROID:
            try:
                # Requires root
                process = await asyncio.create_subprocess_shell(
                    "su -c 'settings put global airplane_mode_on 0 && am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                if process.returncode != 0:
                    self.logger.warning("Root method failed. Opening settings.")
                    await asyncio.create_subprocess_shell("am start -a android.settings.AIRPLANE_MODE_SETTINGS")
                    await self.event_bus.publish("speak", {"text": "I cannot toggle Airplane Mode directly without root, Sir. I have opened the settings for you."})
                else:
                    self.logger.debug("Airplane Mode disabled.")
            except Exception as e:
                self.logger.error(f"Failed to disable Airplane Mode: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Airplane Mode OFF.")
