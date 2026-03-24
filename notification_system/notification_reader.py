import asyncio
import json
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class NotificationReader:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.is_listening = False
        self.seen_notifications = set()
        
        self.event_bus.subscribe("system.notifications.start", self.start_listening)
        self.event_bus.subscribe("system.notifications.stop", self.stop_listening)
        
        self.logger.info("Notification Reader initialized. I am now eavesdropping on your digital life, Sir.")

    async def start_listening(self, data: dict = None):
        if self.is_listening:
            return
        self.is_listening = True
        self.logger.info("Starting Notification Listener Service...")
        asyncio.create_task(self._listen_loop())

    async def stop_listening(self, data: dict = None):
        self.is_listening = False
        self.logger.info("Stopping Notification Listener Service.")

    async def _listen_loop(self):
        # In a Termux environment, we use `termux-notification-list`
        while self.is_listening:
            try:
                process = await asyncio.create_subprocess_exec(
                    "termux-notification-list",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    notifications = json.loads(stdout.decode().strip())
                    
                    for notif in notifications:
                        notif_id = notif.get("id")
                        if notif_id and notif_id not in self.seen_notifications:
                            self.seen_notifications.add(notif_id)
                            # Publish new notification
                            await self.event_bus.publish("notification.received", notif)
                else:
                    self.logger.error(f"Failed to read notifications: {stderr.decode().strip()}")
                
                # Poll every 5 seconds
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error reading notifications: {e}")
                await asyncio.sleep(10)
