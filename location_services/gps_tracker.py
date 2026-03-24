import asyncio
import json
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class GPSTracker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("location.get", self.get_location)
        self.logger.info("GPS Tracker initialized. I know exactly where you are, Sir.")

    async def get_location(self, data: dict):
        self.logger.info("Fetching current GPS coordinates via Termux API...")
        try:
            # Run termux-location (requires location permission)
            # Use network provider for faster, less battery-intensive results, or gps for accuracy
            proc = await asyncio.create_subprocess_exec(
                "termux-location", "-p", "network",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            
            if proc.returncode == 0:
                loc_data = json.loads(stdout.decode('utf-8'))
                lat = loc_data.get("latitude")
                lon = loc_data.get("longitude")
                self.logger.info(f"Location acquired: Lat {lat}, Lon {lon}")
                await self.event_bus.publish("location.result", {"latitude": lat, "longitude": lon})
                await self.event_bus.publish("speak", {"text": f"Your current coordinates are {lat} latitude and {lon} longitude, Sir."})
            else:
                self.logger.error(f"Failed to get location: {stderr.decode()}")
                await self.event_bus.publish("speak", {"text": "I cannot access the GPS module, Sir. Please ensure location permissions are granted."})
        except asyncio.TimeoutError:
            self.logger.error("Location request timed out.")
            await self.event_bus.publish("speak", {"text": "The GPS request timed out, Sir. Are we in a bunker?"})
        except Exception as e:
            self.logger.error(f"Error getting location: {e}")
