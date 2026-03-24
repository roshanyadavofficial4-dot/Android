import asyncio
import shutil
from core.event_bus import EventBus
from core.logger import arya_logger

class StorageMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        
        self.event_bus.subscribe("system.monitor.storage.start", self.start)
        self.event_bus.subscribe("system.monitor.storage.stop", self.stop)
        
        self.logger.info("Storage Monitor initialized. Guarding your precious MBBS PDFs, Sir.")

    async def start(self, data: dict = None):
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.logger.info("Starting Storage monitoring loop.")
        asyncio.create_task(self._monitor_loop())

    async def stop(self, data: dict = None):
        self.is_monitoring = False
        self.logger.info("Stopping Storage monitoring loop.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            try:
                # Check the primary external storage directory on Android
                total, used, free = await asyncio.to_thread(shutil.disk_usage, "/storage/emulated/0")
                
                free_gb = free / (2**30)
                
                # Alert if less than 2 GB remaining
                if free_gb < 2.0:
                    self.logger.warning(f"Low storage space: {free_gb:.2f} GB remaining.")
                    await self.event_bus.publish("speak", {"text": f"Sir, you only have {free_gb:.2f} gigabytes of storage left. Your medical library is consuming the device. I suggest a cleanup."})
                    
            except Exception as e:
                self.logger.error(f"Storage Monitor error: {e}")
                
            # Check storage once an hour
            await asyncio.sleep(3600)
