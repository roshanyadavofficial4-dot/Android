import asyncio
import os
import secrets
import string
from core.event_bus import EventBus
from core.logger import arya_logger

class SatelliteLink:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_active = False
        self.public_url = None
        self.access_token = self._generate_token()
        
        self.event_bus.subscribe("web.satellite.start", self.start_link)
        self.event_bus.subscribe("web.satellite.stop", self.stop_link)
        self.event_bus.subscribe("web.satellite.status", self.get_status)
        
        self.logger.info("Project Satellite-Link (Remote Access) initialized. I'm ready to go global, Sir.")

    def _generate_token(self):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(16))

    async def start_link(self, data: dict):
        if self.is_active:
            return
        
        self.logger.info("Satellite-Link: Establishing secure uplink...")
        await self.event_bus.publish("speak", {"text": "Establishing secure satellite uplink, Sir. Please stand by for global access authorization."})
        
        # In a real Termux environment, the user would run 'lt --port 8080' 
        # For this prototype, we simulate the tunnel URL using the App URL or a placeholder
        # In the AI Studio environment, the app is already public.
        
        self.is_active = True
        self.public_url = os.environ.get("APP_URL", "https://satellite-link.arya.os")
        
        self.logger.info(f"Satellite-Link: Uplink established at {self.public_url}")
        await self.event_bus.publish("speak", {"text": f"Uplink established, Sir. Global access is now active. Your secure token is {self.access_token}."})
        
        await self.event_bus.publish("web.satellite.active", {
            "url": self.public_url,
            "token": self.access_token
        })

    async def stop_link(self, data: dict):
        self.is_active = False
        self.public_url = None
        self.logger.info("Satellite-Link: Uplink terminated.")
        await self.event_bus.publish("speak", {"text": "Satellite uplink terminated, Sir. We are back on the local grid."})
        await self.event_bus.publish("web.satellite.inactive", {})

    async def get_status(self, data: dict):
        await self.event_bus.publish("web.satellite.status_result", {
            "is_active": self.is_active,
            "url": self.public_url,
            "token": self.access_token
        })
