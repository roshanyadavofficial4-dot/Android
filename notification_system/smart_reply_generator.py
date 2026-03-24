import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    from google import genai
except ImportError:
    genai = None

class SmartReplyGenerator:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.api_key = self._load_api_key()
        if genai and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            
        self.event_bus.subscribe("notification.reply.request", self.generate_reply)
        self.event_bus.subscribe("api_keys_updated", self._update_api_keys)
        self.logger.info("Smart Reply Generator initialized. I shall craft your responses with maximum wit and minimum effort, Sir.")

    def _load_api_key(self):
        import json
        try:
            with open("core/data/secrets.json", "r") as f:
                secrets = json.load(f)
                return secrets.get("gemini", os.getenv("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was"))
        except FileNotFoundError:
            return os.getenv("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was")

    async def _update_api_keys(self, payload: dict):
        gemini_key = payload.get("gemini")
        if gemini_key:
            self.api_key = gemini_key
            if genai:
                self.client = genai.Client(api_key=self.api_key)
            self.logger.info("Gemini API Key updated in Smart Reply Generator.")

    async def generate_reply(self, data: dict):
        sender = data.get("sender", "Unknown")
        message = data.get("message", "")
        
        if not message:
            return

        self.logger.info(f"Generating smart reply for message from {sender}...")
        
        if not self.client:
            self.logger.warning("Gemini API not configured. Using fallback static replies.")
            fallback_reply = "I am currently indisposed. A.R.Y.A. will handle this later."
            await self.event_bus.publish("notification.reply.generated", {"sender": sender, "reply": fallback_reply})
            return

        reply = await asyncio.to_thread(self._generate_gemini_reply, sender, message)
        
        if reply:
            self.logger.info(f"Generated reply: {reply}")
            await self.event_bus.publish("notification.reply.generated", {"sender": sender, "reply": reply})

    def _generate_gemini_reply(self, sender: str, message: str) -> str:
        try:
            prompt = (
                f"You are A.R.Y.A., a highly intelligent, slightly sarcastic British AI assistant. "
                f"Your creator (a busy MBBS medical student) just received this message from {sender}: '{message}'. "
                f"Generate a short, polite, but witty quick reply that can be sent via SMS/WhatsApp. "
                f"Keep it under 150 characters."
            )
            
            response = self.client.models.generate_content(
                model='gemini-3.1-flash-preview',
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Gemini API error during smart reply: {e}")
            return "Noted. I will get back to you shortly."
