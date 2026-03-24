import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class FileDeleteEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Critical paths that should NEVER be deleted
        self.protected_paths = [
            "/system",
            "/data",
            "/storage/emulated/0/Android",
            "/storage/emulated/0/DCIM" # Protect the camera roll by default
        ]
        
        self.event_bus.subscribe("file.delete", self.handle_delete)
        self.logger.info("File Delete Engine initialized. Wielding the digital axe with extreme prejudice, Sir.")

    async def handle_delete(self, data: dict):
        file_path = data.get("path")
        if not file_path:
            return

        success = await self.delete_file(file_path)
        if success:
            await self.event_bus.publish("speak", {"text": "File eradicated, Sir. It shall bother us no more."})
        else:
            await self.event_bus.publish("speak", {"text": "I could not delete the file. It appears to be stubbornly clinging to existence."})

    async def delete_file(self, file_path: str) -> bool:
        self.logger.info(f"Deletion requested for: {file_path}")
        
        # SAFETY CHECK 1: Ensure it's an absolute path within user storage
        if not file_path.startswith("/storage/emulated/0/"):
            self.logger.warning(f"Safety Check Failed: {file_path} is outside user storage.")
            return False
            
        # SAFETY CHECK 2: Ensure it's not in a protected directory
        for protected in self.protected_paths:
            if file_path.startswith(protected):
                self.logger.warning(f"Safety Check Failed: {file_path} is in a protected directory ({protected}).")
                return False
                
        # SAFETY CHECK 3: Prevent deletion of APKs unless explicitly bypassed (hardcoded to false here for safety)
        if file_path.lower().endswith(".apk"):
            self.logger.warning(f"Safety Check Failed: Attempted to delete an APK ({file_path}).")
            return False

        return await asyncio.to_thread(self._delete_sync, file_path)

    def _delete_sync(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.logger.info(f"Successfully deleted file: {file_path}")
                    return True
                else:
                    self.logger.warning(f"Cannot delete {file_path}: It is a directory, not a file.")
                    return False
            else:
                self.logger.warning(f"Cannot delete {file_path}: File does not exist.")
                return False
        except PermissionError:
            self.logger.error(f"Permission denied when trying to delete {file_path}.")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting {file_path}: {e}")
            return False
