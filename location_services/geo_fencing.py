import asyncio
import math
from core.event_bus import EventBus
from core.logger import arya_logger

class GeoFencing:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.fences = {} # { "home": {"lat": 12.34, "lon": 56.78, "radius": 100} }
        self.current_location = None
        
        self.event_bus.subscribe("location.geofence.add", self.add_fence)
        self.event_bus.subscribe("location.geofence.remove", self.remove_fence)
        self.event_bus.subscribe("location.gps.update", self.check_fences)
        
        self.logger.info("Geo Fencing initialized. I'll let you know when you cross the line, Sir.")

    async def add_fence(self, data: dict):
        name = data.get("name")
        lat = data.get("lat")
        lon = data.get("lon")
        radius = data.get("radius", 100) # meters
        
        if not name or not lat or not lon:
            self.logger.error("Cannot add geofence without name, lat, and lon.")
            return
            
        self.fences[name] = {"lat": lat, "lon": lon, "radius": radius}
        self.logger.info(f"Geofence added: {name} at {lat}, {lon} with radius {radius}m")
        await self.event_bus.publish("speak", {"text": f"Geofence established for {name}, Sir."})

    async def remove_fence(self, data: dict):
        name = data.get("name")
        if name in self.fences:
            del self.fences[name]
            self.logger.info(f"Geofence removed: {name}")
            await self.event_bus.publish("speak", {"text": f"Geofence removed for {name}, Sir."})

    async def check_fences(self, data: dict):
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not lat or not lon:
            return
            
        self.current_location = (lat, lon)
        
        for name, fence in self.fences.items():
            distance = self._calculate_distance(lat, lon, fence["lat"], fence["lon"])
            
            if distance <= fence["radius"]:
                self.logger.info(f"Entered geofence: {name}")
                await self.event_bus.publish(f"location.geofence.enter.{name}", {})
                await self.event_bus.publish("speak", {"text": f"You have entered the {name} geofence, Sir."})
            else:
                # In a real scenario, track previous state to only trigger on exit
                pass

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        # Haversine formula
        R = 6371000 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
