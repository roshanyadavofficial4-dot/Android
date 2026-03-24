import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class NotificationFilter:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Filter configurations
        self.spam_keywords = ["offer", "discount", "sale", "lottery", "subscribe", "win", "promo"]
        self.priority_keywords = ["urgent", "emergency", "hospital", "patient", "exam", "important", "asap"]
        self.priority_contacts = ["mom", "dad", "professor", "dr.", "doctor", "dean"]
        
        self.event_bus.subscribe("notification.received", self.filter_notification)
        self.logger.info("Notification Filter initialized. I will shield you from the digital noise, Sir.")

    async def filter_notification(self, data: dict):
        app_name = data.get("packageName", "")
        title = data.get("title", "").lower()
        content = data.get("content", "").lower()
        
        # 1. Check for spam
        if any(keyword in content or keyword in title for keyword in self.spam_keywords):
            self.logger.info(f"Spam notification blocked from {title}.")
            return # Drop the event
            
        # 2. Determine Priority
        is_priority = False
        
        # Check priority contacts
        if any(contact in title for contact in self.priority_contacts):
            is_priority = True
            
        # Check priority keywords
        if any(keyword in content for keyword in self.priority_keywords):
            is_priority = True
            
        # 3. Forward the filtered notification
        filtered_data = data.copy()
        filtered_data["is_priority"] = is_priority
        
        self.logger.debug(f"Notification passed filter. Priority: {is_priority}. Title: {data.get('title')}")
        await self.event_bus.publish("notification.filtered", filtered_data)
