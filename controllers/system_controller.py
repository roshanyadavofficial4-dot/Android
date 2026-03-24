import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class SystemController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("controller.brightness.set", self.set_brightness)
        self.event_bus.subscribe("controller.volume.set", self.set_volume)
        self.event_bus.subscribe("controller.flashlight.on", self.turn_on_flashlight)
        self.event_bus.subscribe("controller.flashlight.off", self.turn_off_flashlight)
        self.event_bus.subscribe("controller.data.on", self.turn_on_data)
        self.event_bus.subscribe("controller.data.off", self.turn_off_data)
        
        self.logger.info("System Controller initialized. I now have control over the physical realm via Termux API, Sir.")

    async def turn_on_data(self, data: dict = None):
        self.logger.info("Attempting to enable mobile data, Sir.")
        try:
            # Requires root access in Termux
            proc = await asyncio.create_subprocess_exec(
                "su", "-c", "svc data enable",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.logger.info("Mobile data enabled successfully.")
                await self.event_bus.publish("speak", {"text": "Mobile data is now active, Sir. We are back on the grid."})
            else:
                self.logger.error(f"Failed to enable data (Root required?): {stderr.decode()}")
                await self.event_bus.publish("speak", {"text": "I'm afraid I lack the root authority to toggle mobile data directly, Sir. You'll have to do it manually."})
        except Exception as e:
            self.logger.error(f"Data toggle error: {e}")

    async def turn_off_data(self, data: dict = None):
        self.logger.info("Attempting to disable mobile data.")
        try:
            # Requires root access in Termux
            proc = await asyncio.create_subprocess_exec(
                "su", "-c", "svc data disable",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.logger.info("Mobile data disabled.")
                await self.event_bus.publish("speak", {"text": "Mobile data has been deactivated. Going dark, Sir."})
            else:
                self.logger.error(f"Failed to disable data: {stderr.decode()}")
        except Exception as e:
            self.logger.error(f"Data toggle error: {e}")

    async def set_brightness(self, data: dict):
        level = data.get("level", 50)
        # Convert 0-100 to 0-255 for termux-brightness
        android_level = int((level / 100) * 255)
        self.logger.info(f"Setting brightness to {level}% ({android_level}/255).")

        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-brightness", str(android_level),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.logger.debug("Brightness adjusted successfully.")
            else:
                self.logger.error(f"Failed to set brightness: {stderr.decode()}")
        except Exception as e:
            self.logger.error(f"Error setting brightness: {e}")

    async def set_volume(self, data: dict):
        level = data.get("level", 50)
        # Convert 0-100 to 0-15 (max volume for media stream is usually 15)
        target_vol = int((level / 100) * 15)
        self.logger.info(f"Setting volume to {level}% ({target_vol}/15).")

        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-volume", "music", str(target_vol),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.logger.debug("Volume adjusted. Try not to deafen yourself, Sir.")
            else:
                self.logger.error(f"Failed to set volume: {stderr.decode()}")
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")

    async def turn_on_flashlight(self, data: dict = None):
        self.logger.info("Illuminating the darkness, Sir.")
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-torch", "on",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            self.logger.error(f"Flashlight error: {e}")

    async def turn_off_flashlight(self, data: dict = None):
        self.logger.info("Extinguishing the flashlight.")
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-torch", "off",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            self.logger.error(f"Flashlight error: {e}")
