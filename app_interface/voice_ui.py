import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class VoiceUI:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("ui.voice.activate", self.activate_voice)
        self.event_bus.subscribe("ui.voice.deactivate", self.deactivate_voice)
        self.logger.info("Voice UI initialized. I'm all ears, Sir.")

    async def activate_voice(self, data: dict = None):
        self.logger.info("Activating Voice UI...")
        await self.event_bus.publish("speak", {"text": "Voice interface active. How may I assist you, Sir?"})
        await self.event_bus.publish("voice.listen.start", {})

    async def deactivate_voice(self, data: dict = None):
        self.logger.info("Deactivating Voice UI...")
        await self.event_bus.publish("speak", {"text": "Voice interface deactivated. I shall remain silent, Sir."})
        await self.event_bus.publish("voice.listen.stop", {})
