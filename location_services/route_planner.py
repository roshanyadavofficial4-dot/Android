import asyncio
import subprocess
import urllib.parse
from core.event_bus import EventBus
from core.logger import arya_logger

class RoutePlanner:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("location.route", self.plan_route)
        self.logger.info("Route Planner initialized. Calculating the optimal path, Sir.")

    async def plan_route(self, data: dict):
        destination = data.get("destination")
        if not destination:
            self.logger.warning("No destination provided for routing.")
            return

        self.logger.info(f"Planning route to: {destination}")
        await self.event_bus.publish("speak", {"text": f"Plotting a course to {destination}, Sir."})
        
        try:
            # URL encode the destination
            encoded_dest = urllib.parse.quote(destination)
            # Create a Google Maps intent URL
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={encoded_dest}"
            
            # Open the URL using termux-open, which will launch the Maps app
            proc = await asyncio.create_subprocess_exec(
                "termux-open", maps_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            self.logger.info("Google Maps launched successfully.")
        except Exception as e:
            self.logger.error(f"Failed to launch route planner: {e}")
            await self.event_bus.publish("speak", {"text": "I encountered an error while trying to open the map, Sir."})
