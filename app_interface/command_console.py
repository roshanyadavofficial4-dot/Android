import asyncio
import sys
from core.event_bus import EventBus
from core.logger import arya_logger

class CommandConsole:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_running = False
        
        self.event_bus.subscribe("ui.console.start", self.start)
        self.event_bus.subscribe("ui.console.stop", self.stop)
        self.logger.info("Command Console initialized. Awaiting your typed commands, Sir.")

    async def start(self, data: dict = None):
        if self.is_running:
            return
        self.is_running = True
        self.logger.info("Starting Command Console loop...")
        asyncio.create_task(self._console_loop())

    async def stop(self, data: dict = None):
        self.is_running = False
        self.logger.info("Stopping Command Console loop.")

    async def _console_loop(self):
        while self.is_running:
            try:
                # Read input asynchronously from stdin
                command = await asyncio.to_thread(self._read_input)
                if command:
                    if command.lower() in ["exit", "quit", "stop"]:
                        self.logger.info("Exit command received via console.")
                        await self.event_bus.publish("system.shutdown", {})
                        break
                    
                    self.logger.info(f"Console command received: {command}")
                    await self.event_bus.publish("command.received", {"text": command, "source": "console"})
            except Exception as e:
                self.logger.error(f"Error in console loop: {e}")
                await asyncio.sleep(1)

    def _read_input(self):
        try:
            print("\nA.R.Y.A. > ", end="", flush=True)
            return sys.stdin.readline().strip()
        except Exception:
            return None
