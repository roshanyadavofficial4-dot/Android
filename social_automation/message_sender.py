import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class MessageSender:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("social.message.send", self.route_message)
        
        # Default preferences (could be loaded from a DB later)
        self.user_preferences = {
            "default_platform": "whatsapp",
            "mom": "sms",
            "boss": "telegram"
        }
        
        self.logger.info("Message Sender initialized. The ultimate communication router is online, Sir.")

    async def route_message(self, data: dict):
        contact = data.get("contact", "").lower()
        message = data.get("message", "")
        platform = data.get("platform", "").lower()
        
        if not contact or not message:
            self.logger.error("Cannot send a message without a contact and a message body.")
            return

        # Determine platform based on preference if not explicitly provided
        if not platform:
            platform = self.user_preferences.get(contact, self.user_preferences["default_platform"])

        self.logger.info(f"Routing message to {contact} via {platform.upper()}.")
        
        if platform == "whatsapp":
            await self.event_bus.publish("social.whatsapp.send", {"contact": contact, "message": message})
        elif platform == "telegram":
            await self.event_bus.publish("social.telegram.send", {"contact": contact, "message": message})
        elif platform == "sms":
            await self.event_bus.publish("social.sms.send", {"contact": contact, "message": message})
        elif platform == "instagram":
            # Direct message via Instagram
            await self.event_bus.publish("social.instagram.dm", {"contact": contact, "message": message})
        else:
            self.logger.warning(f"Unsupported platform: {platform}. Defaulting to WhatsApp.")
            await self.event_bus.publish("social.whatsapp.send", {"contact": contact, "message": message})
