import asyncio
import urllib.parse
import json
from core.event_bus import EventBus
from core.logger import arya_logger

class PlaceIdentifier:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("location.place.identify", self.identify_place)
        self.logger.info("Place Identifier initialized. I'll tell you what that building is, Sir.")

    async def identify_place(self, data: dict):
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not lat or not lon:
            self.logger.error("Cannot identify place without coordinates.")
            return

        self.logger.info(f"Identifying place at {lat}, {lon}...")
        await self.event_bus.publish("speak", {"text": "Analyzing the coordinates, Sir. Let's see where you are."})
        
        # In a real scenario, use a reverse geocoding API like Nominatim (OpenStreetMap)
        # Nominatim requires a user-agent
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'ARYA_OS/1.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    display_name = result.get("display_name", "Unknown location")
                    
                    self.logger.info(f"Place identified: {display_name}")
                    await self.event_bus.publish("speak", {"text": f"You appear to be near {display_name}, Sir."})
                    await self.event_bus.publish("location.place.result", {"name": display_name})
                else:
                    self.logger.error(f"Reverse geocoding failed: HTTP {response.status}")
                    await self.event_bus.publish("speak", {"text": "I could not identify the location. You might be off the grid, Sir."})
        except Exception as e:
            self.logger.error(f"Place identification error: {e}")
