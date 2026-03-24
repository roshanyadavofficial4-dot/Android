import asyncio
import time
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import psutil
except ImportError:
    psutil = None

class NetworkMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        self.last_io = None
        self.last_time = None
        
        self.event_bus.subscribe("system.monitor.network.start", self.start)
        self.event_bus.subscribe("system.monitor.network.stop", self.stop)
        
        self.logger.info("Network Monitor initialized. Tracking your digital footprint, Sir.")

    async def start(self, data: dict = None):
        if self.is_monitoring:
            return
        if not psutil:
            self.logger.warning("psutil not installed. Network monitoring disabled.")
            return
            
        self.is_monitoring = True
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        self.logger.info("Starting Network monitoring loop.")
        asyncio.create_task(self._monitor_loop())

    async def stop(self, data: dict = None):
        self.is_monitoring = False
        self.logger.info("Stopping Network monitoring loop.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            try:
                current_io = await asyncio.to_thread(psutil.net_io_counters)
                current_time = time.time()
                
                dt = current_time - self.last_time
                if dt > 0:
                    bytes_recv = current_io.bytes_recv - self.last_io.bytes_recv
                    bytes_sent = current_io.bytes_sent - self.last_io.bytes_sent
                    
                    speed_down = (bytes_recv / dt) / 1024 / 1024 # MB/s
                    speed_up = (bytes_sent / dt) / 1024 / 1024 # MB/s
                    
                    # Log if speed is unusually high (e.g., downloading a massive dataset)
                    if speed_down > 15.0:
                        self.logger.info(f"High download speed detected: {speed_down:.2f} MB/s")
                        
                self.last_io = current_io
                self.last_time = current_time
                
            except Exception as e:
                self.logger.error(f"Network Monitor error: {e}")
                
            await asyncio.sleep(5)
