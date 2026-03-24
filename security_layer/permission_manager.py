import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class PermissionManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("Permission Manager initialized. Ensuring we have the keys to the kingdom, Sir.")
        
        # Check Termux API on startup
        asyncio.create_task(self._check_termux_api())

    async def _check_termux_api(self):
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-info",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self.logger.info("Termux API is installed and accessible.")
            else:
                self.logger.warning("Termux API might not be fully functional. Some features may be limited.")
        except FileNotFoundError:
            self.logger.error("termux-api command not found. Please install it using 'pkg install termux-api'.")
            await self.event_bus.publish("speak", {"text": "Sir, the Termux API package is missing. I cannot control the device hardware without it."})
        except Exception as e:
            self.logger.error(f"Error checking Termux API: {e}")
