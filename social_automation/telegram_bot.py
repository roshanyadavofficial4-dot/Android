import asyncio
import urllib.parse
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID, IS_PC

class TelegramBot:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("social.telegram.send", self.send_message)
        
        self.logger.info("Telegram Bot initialized. Ready to send encrypted snark, Sir.")

    async def send_message(self, data: dict):
        contact = data.get("contact")
        message = data.get("message")
        
        if not contact or not message:
            return

        self.logger.info(f"Sending Telegram message to {contact}...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            if not device:
                self.logger.warning("Device not connected. Simulating Telegram message.")
                return

            try:
                await asyncio.to_thread(self._send_message_sync, device, contact, message)
                await self.event_bus.publish("speak", {"text": f"Telegram message sent to {contact}, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to send Telegram message: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Telegram message.")

    def _send_message_sync(self, device, contact: str, message: str):
        device.app_start("org.telegram.messenger")
        # Click search icon
        device(description="Search").click(timeout=5)
        # Type contact name
        device(className="android.widget.EditText").set_text(contact)
        # Click first result
        device(resourceId="org.telegram.messenger:id/dialog_title", textContains=contact).click(timeout=5)
        # Type message
        device(className="android.widget.EditText").set_text(message)
        # Click send
        device(description="Send").click(timeout=5)
