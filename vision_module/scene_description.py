import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
import os

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class SceneDescriptionEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.api_key = self._load_api_key()
        if self.api_key and genai:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            
        self.event_bus.subscribe("vision.scene.describe", self.describe_scene)
        self.event_bus.subscribe("api_keys_updated", self._update_api_keys)
        self.logger.info("Scene Description Engine initialized. Ready to critique your surroundings, Sir.")

    def _load_api_key(self):
        import json
        try:
            with open("core/data/secrets.json", "r") as f:
                secrets = json.load(f)
                return secrets.get("gemini", os.environ.get("GEMINI_API_KEY"))
        except FileNotFoundError:
            return os.environ.get("GEMINI_API_KEY")

    async def _update_api_keys(self, payload: dict):
        gemini_key = payload.get("gemini")
        if gemini_key:
            self.api_key = gemini_key
            if genai:
                self.client = genai.Client(api_key=self.api_key)
            self.logger.info("Gemini API Key updated in Scene Description Engine.")

    async def describe_scene(self, data: dict):
        image_path = data.get("image_path")
        if not image_path or not os.path.exists(image_path):
            self.logger.error("Invalid image path provided for scene description.")
            return

        self.logger.info(f"Describing scene in {image_path}...")
        await self.event_bus.publish("speak", {"text": "Analyzing the scene, Sir. Let's see what mess you've gotten yourself into."})
        
        if not self.client:
            self.logger.warning("Gemini API key or library missing. Simulating scene description.")
            await self.event_bus.publish("speak", {"text": "I cannot process the image without my Gemini brain, Sir. I assume you are in a room."})
            return

        description = await asyncio.to_thread(self._describe_sync, image_path)
        
        if description:
            self.logger.debug(f"Scene description: {description}")
            await self.event_bus.publish("speak", {"text": description})
        else:
            await self.event_bus.publish("speak", {"text": "I couldn't make sense of the image. It's either too dark, or too chaotic."})

    def _describe_sync(self, image_path: str) -> str:
        try:
            # Read image file
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    "Describe this scene in a concise, slightly sarcastic, and sophisticated manner, addressing the user as 'Sir'."
                ]
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Scene description error: {e}")
            return ""
