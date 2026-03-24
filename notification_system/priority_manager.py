import asyncio
import re
from core.event_bus import EventBus
from core.logger import arya_logger

class PriorityManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("notification.filtered", self.manage_priority)
        self.logger.info("Priority Manager initialized. I will decide who is worthy of your immediate attention, Sir.")

    async def manage_priority(self, data: dict):
        is_priority = data.get("is_priority", False)
        title = data.get("title", "Unknown Sender")
        content = data.get("content", "")
        app_name = data.get("packageName", "an app")
        
        if is_priority:
            self.logger.info(f"High priority notification detected from {title}.")
            
            # Extract context to make the announcement sound natural
            context = self._extract_context(content)
            
            announcement = f"Sir, you have an urgent message from {title} regarding {context}."
            
            # Publish to Voice Engine
            await self.event_bus.publish("speak", {"text": announcement})
            
            # Optionally, trigger the smart reply generator to prepare a response
            await self.event_bus.publish("notification.reply.request", {
                "sender": title,
                "message": content
            })
        else:
            self.logger.debug(f"Low priority notification from {title} filed away silently.")
            # We could store it in a digest to read later

    def _extract_context(self, content: str) -> str:
        """
        Attempts to extract the core subject of the message to make the TTS sound natural.
        """
        lower_content = content.lower()
        
        if "exam" in lower_content:
            return "an upcoming exam"
        elif "patient" in lower_content or "hospital" in lower_content:
            return "a medical situation"
        elif "urgent" in lower_content:
            return "an urgent matter"
        
        # Fallback: just read the first few words or a summarized version
        words = content.split()
        if len(words) > 8:
            return " ".join(words[:8]) + "..."
        return content
