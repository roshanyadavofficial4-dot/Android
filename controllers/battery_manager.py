import asyncio
import json
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class BatteryManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_monitoring = False
        self.alert_threshold = 20  # Warn at 20%
        self.critical_threshold = 5 # Warn at 5%
        self.has_warned_low = False
        self.has_warned_critical = False
        
        self.logger.info("Battery Manager initialized. Keeping an eye on our life support, Sir.")

    async def start_monitoring(self):
        if self.is_monitoring:
            return
        self.is_monitoring = True
        self.logger.info("Battery monitoring started.")
        asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        self.is_monitoring = False
        self.logger.info("Battery monitoring stopped.")

    async def _monitor_loop(self):
        while self.is_monitoring:
            if IS_ANDROID:
                try:
                    process = await asyncio.create_subprocess_exec(
                        "termux-battery-status",
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        status = json.loads(stdout.decode())
                        percentage = status.get("percentage", 100)
                        status_text = status.get("status", "UNKNOWN")
                        is_charging = status_text in ["CHARGING", "FULL"]
                        
                        self.logger.debug(f"Battery at {percentage}%. Charging: {is_charging}")
                        
                        # Publish battery update for TriggerDetector
                        await self.event_bus.publish("system.battery.update", {
                            "level": percentage,
                            "is_charging": is_charging
                        })
                        
                        if is_charging:
                            # Reset warnings if plugged in
                            self.has_warned_low = False
                            self.has_warned_critical = False
                        else:
                            if percentage <= self.critical_threshold and not self.has_warned_critical:
                                self.logger.warning("Battery critical!")
                                await self.event_bus.publish("speak", {
                                    "text": f"Sir, battery is at a critical {percentage} percent. I suggest finding a charger before I die."
                                })
                                self.has_warned_critical = True
                            elif percentage <= self.alert_threshold and not self.has_warned_low:
                                self.logger.warning("Battery low.")
                                await self.event_bus.publish("speak", {
                                    "text": f"Pardon the interruption, Sir, but the battery has dropped to {percentage} percent."
                                })
                                self.has_warned_low = True
                                
                except Exception as e:
                    self.logger.error(f"Failed to read battery status: {e}")
            else:
                self.logger.debug("Not on Android. Assuming infinite power.")
                
            # Check every 60 seconds
            await asyncio.sleep(60)
