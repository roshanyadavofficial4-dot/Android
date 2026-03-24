import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class FileRenameEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("file.rename", self.handle_rename)
        self.logger.info("File Rename Engine initialized. Ready to fix your terrible naming conventions, Sir.")

    async def handle_rename(self, data: dict):
        source = data.get("source")
        new_name = data.get("new_name")
        if not source or not new_name:
            self.logger.error("Source or new_name missing for rename operation.")
            return

        self.logger.info(f"Renaming {source} to {new_name}...")
        success = await asyncio.to_thread(self._rename_sync, source, new_name)
        if success:
            await self.event_bus.publish("speak", {"text": "File renamed successfully, Sir."})
        else:
            await self.event_bus.publish("speak", {"text": "Failed to rename the file. Please check the logs."})

    def _rename_sync(self, source: str, new_name: str) -> bool:
        try:
            if not os.path.exists(source):
                self.logger.error(f"Source file does not exist: {source}")
                return False
            
            directory = os.path.dirname(source)
            destination = os.path.join(directory, new_name)
            
            if os.path.exists(destination):
                self.logger.error(f"Destination file already exists: {destination}")
                return False
                
            os.rename(source, destination)
            return True
        except Exception as e:
            self.logger.error(f"Error renaming file: {e}")
            return False
