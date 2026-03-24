import os
import shutil
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class FileCopyMoveEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("file.copy", self.handle_copy)
        self.event_bus.subscribe("file.move", self.handle_move)
        self.logger.info("File Copy/Move Engine initialized. Ready to shuffle your data, Sir.")

    async def handle_copy(self, data: dict):
        source = data.get("source")
        destination = data.get("destination")
        if not source or not destination:
            self.logger.error("Source or destination missing for copy operation.")
            return

        self.logger.info(f"Copying {source} to {destination}...")
        success = await asyncio.to_thread(self._copy_sync, source, destination)
        if success:
            await self.event_bus.publish("speak", {"text": "File copied successfully, Sir."})
        else:
            await self.event_bus.publish("speak", {"text": "Failed to copy the file. Please check the logs."})

    async def handle_move(self, data: dict):
        source = data.get("source")
        destination = data.get("destination")
        if not source or not destination:
            self.logger.error("Source or destination missing for move operation.")
            return

        self.logger.info(f"Moving {source} to {destination}...")
        success = await asyncio.to_thread(self._move_sync, source, destination)
        if success:
            await self.event_bus.publish("speak", {"text": "File moved successfully, Sir."})
        else:
            await self.event_bus.publish("speak", {"text": "Failed to move the file. Please check the logs."})

    def _copy_sync(self, source: str, destination: str) -> bool:
        try:
            if not os.path.exists(source):
                self.logger.error(f"Source file does not exist: {source}")
                return False
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            return True
        except Exception as e:
            self.logger.error(f"Error copying file: {e}")
            return False

    def _move_sync(self, source: str, destination: str) -> bool:
        try:
            if not os.path.exists(source):
                self.logger.error(f"Source file does not exist: {source}")
                return False
            shutil.move(source, destination)
            return True
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
            return False
