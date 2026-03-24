import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class TravelAssistant:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("location.travel.assist", self.assist_travel)
        self.logger.info("Travel Assistant initialized. I'll make sure you don't get lost, Sir.")

    async def assist_travel(self, data: dict):
        destination = data.get("destination")
        if not destination:
            self.logger.error("No destination provided for travel assistance.")
            return

        self.logger.info(f"Providing travel assistance for: {destination}")
        await self.event_bus.publish("speak", {"text": f"Preparing travel itinerary for {destination}, Sir. I'll check the weather and traffic."})
        
        # 1. Fetch weather for destination
        await self.event_bus.publish("web.weather.fetch", {"location": destination})
        
        # 2. Plan route (assuming current location is known or can be fetched)
        # In a real scenario, we'd fetch current GPS coordinates first
        await self.event_bus.publish("location.route.plan", {"destination": destination})
        
        # 3. Fetch some basic info about the place
        await self.event_bus.publish("web.knowledge.query", {"query": f"Things to do in {destination}", "source": "wikipedia"})
