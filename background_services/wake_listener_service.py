import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class WakeListenerService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_running = True
        self.logger.info("Wake Listener Service initialized. I am always listening, Sir.")
        
        # Start the background heartbeat
        asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        while self.is_running:
            # Emit a heartbeat event every 60 seconds to keep the OS alive
            await self.event_bus.publish("system.heartbeat", {"status": "alive"})
            await asyncio.sleep(60)
