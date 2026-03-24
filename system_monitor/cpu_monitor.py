import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import psutil
except ImportError:
    psutil = None

class CPUMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        
        self.event_bus.subscribe("system.monitor.cpu.start", self.start)
        self.event_bus.subscribe("system.monitor.cpu.stop", self.stop)
        self.event_bus.subscribe("system.status.report", self.report_status)
        
        self.logger.info("CPU Monitor initialized. I will ensure your processor doesn't melt, Sir.")

    async def report_status(self, data: dict):
        if not psutil:
            await self.event_bus.publish("speak", {"text": "I cannot check system status without the psutil library, Sir."})
            return
        try:
            cpu = await asyncio.to_thread(psutil.cpu_percent, interval=0.5)
            ram = await asyncio.to_thread(psutil.virtual_memory)
            ram_percent = ram.percent
            await self.event_bus.publish("speak", {"text": f"System status: CPU is at {cpu} percent, and RAM usage is at {ram_percent} percent. All systems nominal, Sir."})
        except Exception as e:
            self.logger.error(f"Error reporting status: {e}")

    async def start(self, data: dict = None):
        if self.is_monitoring:
            return
        if not psutil:
            self.logger.warning("psutil not installed. CPU monitoring disabled.")
            return
            
        self.is_monitoring = True
        self.logger.info("Starting CPU monitoring loop.")
        asyncio.create_task(self._monitor_loop())

    async def stop(self, data: dict = None):
        self.is_monitoring = False
        self.logger.info("Stopping CPU monitoring loop.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            try:
                # Offload blocking psutil call to a thread
                cpu_usage = await asyncio.to_thread(psutil.cpu_percent, interval=1)
                
                if cpu_usage > 90:
                    self.logger.warning(f"High CPU usage detected: {cpu_usage}%")
                    await self.event_bus.publish("speak", {"text": f"Sir, CPU usage is at {cpu_usage} percent. The processor is sweating. I suggest we cool down."})
                    
            except Exception as e:
                self.logger.error(f"CPU Monitor error: {e}")
                
            await asyncio.sleep(10)
