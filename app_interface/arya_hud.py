import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class AryaHUD:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("A.R.Y.A. HUD initialized. Visuals are online, Sir.")
        self.display_status()

    def display_status(self):
        print("========================================")
        print("      A.R.Y.A. OS - Systems Active      ")
        print("========================================")
        print(" Medical & System Diagnostics: ONLINE   ")
        print(" Waiting for command...                 ")
        print("========================================")
