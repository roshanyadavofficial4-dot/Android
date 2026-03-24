import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from file_system.storage_scanner import StorageScanner

class LargeFileDetector:
    def __init__(self, event_bus: EventBus, scanner: StorageScanner):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.scanner = scanner
        
        self.event_bus.subscribe("file.find_large", self.handle_find_large)
        self.logger.info("Large File Detector initialized. Ready to find the space hogs, Sir.")

    async def handle_find_large(self, data: dict):
        path = data.get("path")
        min_size_mb = data.get("min_size_mb", 100) # Default 100MB
        
        await self.event_bus.publish("speak", {"text": f"Scanning for files larger than {min_size_mb} megabytes, Sir."})
        
        large_files = await self.find_large_files(path, min_size_mb)
        
        if large_files:
            self.logger.info(f"Found {len(large_files)} large files.")
            await self.event_bus.publish("speak", {"text": f"I found {len(large_files)} massive files consuming your storage. Shall I list them?"})
            for file, size in large_files[:5]:
                self.logger.debug(f"Large file: {file} ({size:.2f} MB)")
        else:
            self.logger.info("No large files found.")
            await self.event_bus.publish("speak", {"text": "No exceptionally large files found, Sir. Your storage is safe for now."})

    async def find_large_files(self, path: str = None, min_size_mb: int = 100) -> list:
        all_files = await self.scanner.scan(path)
        return await asyncio.to_thread(self._find_large_sync, all_files, min_size_mb)

    def _find_large_sync(self, files: list, min_size_mb: int) -> list:
        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []
        for f in files:
            try:
                size = os.path.getsize(f)
                if size >= min_size_bytes:
                    large_files.append((f, size / (1024 * 1024)))
            except OSError:
                continue
        
        # Sort by size descending
        large_files.sort(key=lambda x: x[1], reverse=True)
        return large_files
