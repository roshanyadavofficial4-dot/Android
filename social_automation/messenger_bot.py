import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID

class MessengerBot:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("social.messenger.send", self.send_message)
        
        self.logger.info("Messenger Bot initialized. Ready to interface with the Zuckerberg empire, Sir.")

    async def send_message(self, data: dict):
        contact = data.get("contact")
        message = data.get("message")
        
        if not contact or not message:
            return

        self.logger.info(f"Sending Messenger message to {contact}...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            if not device:
                self.logger.warning("Device not connected. Simulating Messenger message.")
                return

            try:
                await asyncio.to_thread(self._send_message_sync, device, contact, message)
                await self.event_bus.publish("speak", {"text": f"Messenger message sent to {contact}, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to send Messenger message: {e}")
        else:
            self.logger.warning("Not on Android. Simulating Messenger message.")

    def _send_message_sync(self, device, contact: str, message: str):
        device.app_start("com.facebook.orca")
        # Click search
        device(description="Search").click(timeout=5)
        # Type contact
        device(className="android.widget.EditText").set_text(contact)
        # Click first result
        device(text=contact, className="android.widget.TextView").click(timeout=5)
        # Type message
        device(className="android.widget.EditText").set_text(message)
        # Click send
        device(description="Send").click(timeout=5)
