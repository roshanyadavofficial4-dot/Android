import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class BackgroundWorker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_running = False
        
        self.event_bus.subscribe("system.worker.start", self.start)
        self.event_bus.subscribe("system.worker.stop", self.stop)
        self.logger.info("Background Worker initialized. I am the unseen hand, Sir.")

    async def start(self, data: dict = None):
        if self.is_running:
            return
        self.is_running = True
        self.logger.info("Starting background worker loop...")
        asyncio.create_task(self._worker_loop())

    async def stop(self, data: dict = None):
        self.is_running = False
        self.logger.info("Stopping background worker loop.")

    async def _worker_loop(self):
        while self.is_running:
            try:
                # Perform periodic background tasks here
                # e.g., checking for updates, cleaning up temp files, etc.
                await asyncio.sleep(60) # Run every minute
            except Exception as e:
                self.logger.error(f"Error in background worker: {e}")
                await asyncio.sleep(10)
