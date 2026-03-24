import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID, IS_PC

if IS_PC:
    try:
        import psutil
    except ImportError:
        psutil = None

class TemperatureMonitor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        
        self.event_bus.subscribe("system.monitor.temp.start", self.start)
        self.event_bus.subscribe("system.monitor.temp.stop", self.stop)
        
        self.logger.info("Temperature Monitor initialized. I will let you know if the device is about to combust, Sir.")

    async def start(self, data: dict = None):
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.logger.info("Starting Temperature monitoring loop.")
        asyncio.create_task(self._monitor_loop())

    async def stop(self, data: dict = None):
        self.is_monitoring = False
        self.logger.info("Stopping Temperature monitoring loop.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            try:
                temp = await asyncio.to_thread(self._get_temperature)
                
                if temp and temp > 45.0:
                    self.logger.warning(f"High device temperature: {temp}°C")
                    await self.event_bus.publish("speak", {"text": f"Sir, the device temperature is {temp} degrees Celsius. The AI models are running a bit too hot. I recommend a brief pause."})
                    
            except Exception as e:
                self.logger.error(f"Temperature Monitor error: {e}")
                
            await asyncio.sleep(30)

    def _get_temperature(self):
        if IS_ANDROID:
            # Android thermal zone approach
            # This reads the raw thermal zone files exposed by the Linux kernel on Android
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp_str = f.read().strip()
                    temp = int(temp_str)
                    # Sometimes it's reported in millidegrees Celsius
                    if temp > 1000:
                        return temp / 1000.0
                    return float(temp)
            except Exception:
                # Fallback if thermal_zone0 is inaccessible
                return None
        elif IS_PC:
            if psutil and hasattr(psutil, 'sensors_temperatures'):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Just grab the first available temperature sensor
                        first_sensor = list(temps.values())[0]
                        if first_sensor:
                            return float(first_sensor[0].current)
                except Exception:
                    pass
            return None
