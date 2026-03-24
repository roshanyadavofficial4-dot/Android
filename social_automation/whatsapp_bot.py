import asyncio
import webbrowser
import urllib.parse
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID, IS_PC

class WhatsAppBot:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("social.whatsapp.send", self.send_message)
        self.event_bus.subscribe("social.whatsapp.read_last", self.read_last_message)
        self.event_bus.subscribe("social.whatsapp.send_voice", self.send_voice_note)
        
        self.logger.info("WhatsApp Bot initialized. Ready to spam your contacts, Sir.")

    async def send_message(self, data: dict):
        contact = data.get("contact")
        message = data.get("message")
        
        if not contact or not message:
            self.logger.warning("Cannot send WhatsApp message without contact and message.")
            return

        self.logger.info(f"Sending WhatsApp message to {contact}...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            
            if not device:
                self.logger.warning("Device not connected. Simulating WhatsApp message send.")
                await self.event_bus.publish("speak", {"text": f"Simulating message to {contact}. They wouldn't have replied anyway, Sir."})
                return

            try:
                await asyncio.to_thread(self._send_message_sync, device, contact, message)
                await self.event_bus.publish("speak", {"text": f"Message sent to {contact}. Let's hope they appreciate the effort."})
            except Exception as e:
                self.logger.error(f"Failed to send WhatsApp message: {e}")
                await self.event_bus.publish("speak", {"text": "Failed to send the WhatsApp message. The app is being uncooperative."})
        elif IS_PC:
            try:
                # Open WhatsApp Web or Desktop app with pre-filled message
                # Note: This requires the user to manually click "Send" on PC
                encoded_msg = urllib.parse.quote(message)
                url = f"whatsapp://send?text={encoded_msg}"
                webbrowser.open(url)
                await self.event_bus.publish("speak", {"text": f"I've prepared the message to {contact} on your PC. You'll have to press send yourself, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to open WhatsApp on PC: {e}")

    def _send_message_sync(self, device, contact: str, message: str):
        # Launch WhatsApp
        device.app_start("com.whatsapp")
        device(resourceId="com.whatsapp:id/menuitem_search").click(timeout=5)
        device(resourceId="com.whatsapp:id/search_src_text").set_text(contact)
        
        # Click the first contact result
        device(resourceId="com.whatsapp:id/contactpicker_row_name", text=contact).click(timeout=5)
        
        # Type and send
        device(resourceId="com.whatsapp:id/entry").set_text(message)
        device(resourceId="com.whatsapp:id/send").click(timeout=5)

    async def read_last_message(self, data: dict):
        contact = data.get("contact")
        self.logger.info(f"Reading last WhatsApp message from {contact}...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            
            if not device:
                self.logger.warning("Device not connected. Cannot read messages.")
                return
                
            try:
                message_text = await asyncio.to_thread(self._read_last_message_sync, device, contact)
                if message_text:
                    await self.event_bus.publish("speak", {"text": f"{contact} said: {message_text}"})
                else:
                    await self.event_bus.publish("speak", {"text": f"I couldn't find any recent messages from {contact}, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to read WhatsApp message: {e}")
        elif IS_PC:
            self.logger.warning("Cannot read WhatsApp messages natively on PC.")
            await self.event_bus.publish("speak", {"text": f"I cannot read your WhatsApp messages on the PC, Sir. Privacy and all that."})

    def _read_last_message_sync(self, device, contact: str) -> str:
        device.app_start("com.whatsapp")
        device(resourceId="com.whatsapp:id/menuitem_search").click(timeout=5)
        device(resourceId="com.whatsapp:id/search_src_text").set_text(contact)
        device(resourceId="com.whatsapp:id/contactpicker_row_name", text=contact).click(timeout=5)
        
        # Get all message text views and return the last one
        messages = device(resourceId="com.whatsapp:id/message_text")
        if messages.exists and len(messages) > 0:
            return messages[len(messages) - 1].get_text()
        return None

    async def send_voice_note(self, data: dict):
        contact = data.get("contact")
        duration = data.get("duration", 5) # seconds
        self.logger.info(f"Sending {duration}s voice note to {contact}...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            if not device:
                self.logger.warning("Device not connected. Simulating voice note.")
                return
                
            try:
                await asyncio.to_thread(self._send_voice_note_sync, device, contact, duration)
                await self.event_bus.publish("speak", {"text": f"Voice note sent to {contact}. I hope your diction was acceptable, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to send voice note: {e}")
        elif IS_PC:
            self.logger.warning("Cannot send voice notes natively on PC.")
            await self.event_bus.publish("speak", {"text": f"I cannot send voice notes from the PC, Sir."})

    def _send_voice_note_sync(self, device, contact: str, duration: int):
        device.app_start("com.whatsapp")
        device(resourceId="com.whatsapp:id/menuitem_search").click(timeout=5)
        device(resourceId="com.whatsapp:id/search_src_text").set_text(contact)
        device(resourceId="com.whatsapp:id/contactpicker_row_name", text=contact).click(timeout=5)
        
        # Long press the voice note button
        voice_btn = device(resourceId="com.whatsapp:id/voice_note_btn")
        voice_btn.long_click(duration=duration)
