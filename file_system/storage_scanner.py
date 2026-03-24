import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class StorageScanner:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.default_path = "/storage/emulated/0/"
        self.logger.info("Storage Scanner initialized. Preparing to index your digital hoarding habits, Sir.")

    async def scan(self, path: str = None) -> list:
        target_path = path or self.default_path
        self.logger.info(f"Initiating recursive scan of {target_path}...")
        
        # Run the blocking os.walk in a separate thread
        files = await asyncio.to_thread(self._scan_sync, target_path)
        
        self.logger.info(f"Scan complete. Discovered {len(files)} files. How you find anything is beyond me.")
        return files

    def _scan_sync(self, target_path: str) -> list:
        file_list = []
        if not os.path.exists(target_path):
            self.logger.warning(f"Path {target_path} does not exist. Are we hallucinating directories now, Sir?")
            return file_list

        try:
            # Using os.scandir for better performance than os.walk where possible, 
            # but os.walk is simpler for deep recursion. We'll use os.walk for reliability.
            for root, _, files in os.walk(target_path):
                # Skip hidden directories to save time and sanity
                if '/.' in root:
                    continue
                for file in files:
                    # Skip hidden files
                    if not file.startswith('.'):
                        file_list.append(os.path.join(root, file))
        except PermissionError:
            self.logger.warning(f"Permission denied while scanning {target_path}. Android security strikes again.")
        except Exception as e:
            self.logger.error(f"Error during storage scan: {e}")
            
        return file_list
