import traceback
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class ErrorHandler:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("system_error", self.handle_error)
        self.logger.info("Error Handler initialized. I shall clean up the messes, as usual, Sir.")

    async def handle_error(self, error_data: dict):
        error = error_data.get("error")
        context = error_data.get("context", "Unknown context")
        
        error_msg = f"An error occurred in {context}: {str(error)}"
        self.logger.error(error_msg)
        self.logger.error(traceback.format_exc())
        
        # Notify the user via TTS or UI
        await self.event_bus.publish("speak", {
            "text": f"It appears something has gone terribly wrong in {context}, Sir. I've logged the failure for your eventual perusal."
        })
        
        # Attempt recovery if possible
        await self.attempt_recovery(context, error)

    async def attempt_recovery(self, context: str, error: Exception):
        self.logger.info(f"Attempting to recover from failure in {context}...")
        
        # Trigger self-healing protocol
        trace = traceback.format_exc()
        await self.event_bus.publish("system.error.heal", {
            "traceback": trace,
            "context": context,
            "error_msg": str(error)
        })
        
        await asyncio.sleep(0.1)
        self.logger.info("Recovery attempt initiated. Let's hope for the best.")
