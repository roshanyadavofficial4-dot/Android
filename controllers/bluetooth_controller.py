import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class BluetoothController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("controller.bluetooth.on", self.turn_on)
        self.event_bus.subscribe("controller.bluetooth.off", self.turn_off)
        
        self.logger.info("Bluetooth Controller initialized. Ready to pair with your inferior devices, Sir.")

    async def turn_on(self, data: dict = None):
        self.logger.info("Enabling Bluetooth...")
        if IS_ANDROID:
            try:
                # Try root method first
                process = await asyncio.create_subprocess_shell(
                    "su -c 'svc bluetooth enable'",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    self.logger.warning("Root method failed. Opening Bluetooth settings instead.")
                    await asyncio.create_subprocess_shell("am start -a android.settings.BLUETOOTH_SETTINGS")
                    await self.event_bus.publish("speak", {"text": "I cannot toggle Bluetooth directly without root, Sir. I have opened the settings for you."})
                else:
                    self.logger.debug("Bluetooth enabled.")
            except Exception as e:
                self.logger.error(f"Failed to enable Bluetooth: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Bluetooth ON.")

    async def turn_off(self, data: dict = None):
        self.logger.info("Disabling Bluetooth...")
        if IS_ANDROID:
            try:
                # Try root method first
                process = await asyncio.create_subprocess_shell(
                    "su -c 'svc bluetooth disable'",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    self.logger.warning("Root method failed. Opening Bluetooth settings instead.")
                    await asyncio.create_subprocess_shell("am start -a android.settings.BLUETOOTH_SETTINGS")
                    await self.event_bus.publish("speak", {"text": "I cannot toggle Bluetooth directly without root, Sir. I have opened the settings for you."})
                else:
                    self.logger.debug("Bluetooth disabled.")
            except Exception as e:
                self.logger.error(f"Failed to disable Bluetooth: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Bluetooth OFF.")
