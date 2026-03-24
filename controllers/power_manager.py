import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class PowerManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_power_save = False
        
        self.event_bus.subscribe("system.power.save_on", self.enable_power_save)
        self.event_bus.subscribe("system.power.save_off", self.disable_power_save)
        
        self.logger.info("Power Manager initialized. Monitoring energy consumption, Sir.")

    async def enable_power_save(self, data: dict):
        self.is_power_save = True
        self.logger.info("Power Save Mode: ENABLED. Throttling background services.")
        
        # Publish events to throttle other modules
        await self.event_bus.publish("system.monitor.throttle", {"interval": 30}) # Poll every 30s instead of 5s
        await self.event_bus.publish("voice.wake_word.throttle", {"sensitivity": 0.3}) # Lower sensitivity to save CPU
        await self.event_bus.publish("vision.gaze.stop", {}) # Force stop gaze tracking
        
        await self.event_bus.publish("speak", {"text": "Power save mode engaged. I've throttled background monitoring and disabled heavy vision modules to conserve battery, Sir."})

    async def disable_power_save(self, data: dict):
        self.is_power_save = False
        self.logger.info("Power Save Mode: DISABLED. Restoring full performance.")
        
        await self.event_bus.publish("system.monitor.throttle", {"interval": 5})
        await self.event_bus.publish("voice.wake_word.throttle", {"sensitivity": 0.5})
        
        await self.event_bus.publish("speak", {"text": "Full power restored. All systems are back to peak performance, Sir."})
