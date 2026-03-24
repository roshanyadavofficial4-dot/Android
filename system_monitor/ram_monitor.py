import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import psutil
except ImportError:
    psutil = None

class RAMMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        
        self.event_bus.subscribe("system.monitor.ram.start", self.start)
        self.event_bus.subscribe("system.monitor.ram.stop", self.stop)
        
        self.logger.info("RAM Monitor initialized. I will ruthlessly terminate memory hogs, Sir.")

    async def start(self, data: dict = None):
        if self.is_monitoring:
            return
        if not psutil:
            self.logger.warning("psutil not installed. RAM monitoring disabled.")
            return
            
        self.is_monitoring = True
        self.logger.info("Starting RAM monitoring loop.")
        asyncio.create_task(self._monitor_loop())

    async def stop(self, data: dict = None):
        self.is_monitoring = False
        self.logger.info("Stopping RAM monitoring loop.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            try:
                mem = await asyncio.to_thread(psutil.virtual_memory)
                
                # If RAM usage exceeds 85%
                if mem.percent > 85:
                    self.logger.warning(f"Critically low RAM detected: {mem.percent}% used.")
                    await self.event_bus.publish("speak", {"text": "Memory is critically low, Sir. Initiating background app purge to free up space."})
                    
                    # Trigger the app_closer.py in the app_automation module
                    await self.event_bus.publish("app.close.background", {})
                    
                    # Sleep longer after a purge to let the system recover
                    await asyncio.sleep(30)
                    
            except Exception as e:
                self.logger.error(f"RAM Monitor error: {e}")
                
            await asyncio.sleep(15)
