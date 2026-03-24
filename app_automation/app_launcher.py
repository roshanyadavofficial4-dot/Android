import asyncio
import webbrowser
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID, IS_PC

class AppLauncher:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("app.launch", self.launch_app)
        self.event_bus.subscribe("app.close", self.close_app)
        
        # A dictionary mapping common names to their Android package names
        self.app_map = {
            "youtube": "com.google.android.youtube",
            "whatsapp": "com.whatsapp",
            "chrome": "com.android.chrome",
            "spotify": "com.spotify.music",
            "instagram": "com.instagram.android",
            "settings": "com.android.settings",
            "camera": "com.android.camera2", # Varies by device, fallback may be needed
            "maps": "com.google.android.apps.maps"
        }
        
        # PC URL equivalents
        self.pc_url_map = {
            "youtube": "https://www.youtube.com",
            "whatsapp": "whatsapp://", # or "https://web.whatsapp.com"
            "chrome": "https://www.google.com",
            "spotify": "spotify://",
            "instagram": "https://www.instagram.com",
            "settings": "ms-settings:" if IS_PC else "",
            "maps": "https://maps.google.com"
        }
        self.logger.info("App Launcher initialized. Ready to summon your digital distractions, Sir.")

    async def launch_app(self, data: dict):
        app_name = data.get("app_name", "").lower()
        
        if IS_ANDROID:
            package_name = data.get("package_name") or self.app_map.get(app_name)

            if not package_name:
                self.logger.warning(f"Unknown app requested: {app_name}")
                await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Failed", "reason": "Unknown app package"})
                await self.event_bus.publish("speak", {"text": f"I'm afraid I don't know the package name for {app_name}, Sir. You'll have to open it yourself like a peasant."})
                return

            self.logger.info(f"Launching {app_name} ({package_name})...")
            device = self.driver.get_device()
            
            if device:
                try:
                    await asyncio.to_thread(device.app_start, package_name)
                    await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Success", "app": app_name})
                    await self.event_bus.publish("speak", {"text": f"Opening {app_name}, Sir."})
                except Exception as e:
                    self.logger.error(f"Failed to launch {app_name}: {e}")
                    await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Failed", "reason": str(e)})
            else:
                self.logger.warning("Device not connected. Simulating app launch.")
                await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Success", "simulated": True})
        
        elif IS_PC:
            url = self.pc_url_map.get(app_name)
            if not url:
                self.logger.warning(f"Unknown app requested for PC: {app_name}")
                await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Failed", "reason": "Unknown app URL"})
                await self.event_bus.publish("speak", {"text": f"I don't have a PC shortcut for {app_name}, Sir."})
                return
                
            self.logger.info(f"Launching {app_name} on PC ({url})...")
            try:
                webbrowser.open(url)
                await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Success", "app": app_name})
                await self.event_bus.publish("speak", {"text": f"Opening {app_name} on your PC, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to launch {app_name} on PC: {e}")
                await self.event_bus.publish("action_result", {"action": "app.launch", "status": "Failed", "reason": str(e)})

    async def close_app(self, data: dict):
        app_name = data.get("app_name", "").lower()
        
        if IS_ANDROID:
            package_name = data.get("package_name") or self.app_map.get(app_name)
            
            if not package_name:
                return

            self.logger.info(f"Closing {app_name} ({package_name})...")
            device = self.driver.get_device()
            
            if device:
                try:
                    await asyncio.to_thread(device.app_stop, package_name)
                    await self.event_bus.publish("action_result", {"action": "app.close", "status": "Success", "app": app_name})
                except Exception as e:
                    self.logger.error(f"Failed to close {app_name}: {e}")
                    await self.event_bus.publish("action_result", {"action": "app.close", "status": "Failed", "reason": str(e)})
        elif IS_PC:
            self.logger.info(f"Closing {app_name} on PC is not natively supported via webbrowser.")
            await self.event_bus.publish("speak", {"text": f"I cannot close {app_name} on your PC. You'll have to click the X yourself, Sir."})
