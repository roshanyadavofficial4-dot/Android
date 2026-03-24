import asyncio
import os
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class GalleryManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("media.gallery.open", self.open_gallery)
        self.logger.info("Gallery Manager initialized. I'll fetch your digital memories, Sir.")

    async def open_gallery(self, data: dict):
        self.logger.info("Opening the gallery app.")
        await self.event_bus.publish("speak", {"text": "Opening your photo gallery, Sir. Let's take a trip down memory lane."})
        
        # In Android, we can launch the default gallery using an Intent
        try:
            process = await asyncio.create_subprocess_exec(
                "am", "start", "-a", "android.intent.action.VIEW", "-t", "image/*",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Failed to open gallery: {stderr.decode().strip()}")
                await self.event_bus.publish("speak", {"text": "I encountered an error trying to open the gallery. Perhaps you don't have one installed."})
        except Exception as e:
            self.logger.error(f"Gallery launch error: {e}")
