import os
import hashlib
import asyncio
from collections import defaultdict
from core.event_bus import EventBus
from core.logger import arya_logger
from file_system.storage_scanner import StorageScanner

class DuplicateFinder:
    def __init__(self, event_bus: EventBus, scanner: StorageScanner):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.scanner = scanner
        
        self.event_bus.subscribe("file.find_duplicates", self.handle_find_duplicates)
        self.logger.info("Duplicate Finder initialized. Ready to expose your redundant file hoarding, Sir.")

    async def handle_find_duplicates(self, data: dict):
        path = data.get("path")
        await self.event_bus.publish("speak", {"text": "Scanning for duplicate files, Sir. Prepare to be judged for your digital clutter."})
        
        duplicates = await self.find_duplicates(path)
        
        total_wasted_space = sum([os.path.getsize(dupes[0]) * (len(dupes) - 1) for dupes in duplicates.values()])
        wasted_mb = total_wasted_space / (1024 * 1024)
        
        if duplicates:
            self.logger.info(f"Found {len(duplicates)} sets of duplicates, wasting {wasted_mb:.2f} MB.")
            await self.event_bus.publish("speak", {"text": f"I found {len(duplicates)} duplicate files, wasting approximately {wasted_mb:.2f} megabytes of space. Shall I purge the clones?"})
        else:
            self.logger.info("No duplicates found.")
            await self.event_bus.publish("speak", {"text": "Miraculously, I found no duplicate files. Your storage is surprisingly tidy, Sir."})

    async def find_duplicates(self, path: str = None) -> dict:
        all_files = await self.scanner.scan(path)
        return await asyncio.to_thread(self._find_duplicates_sync, all_files)

    def _find_duplicates_sync(self, files: list) -> dict:
        # Step 1: Group by file size to quickly eliminate unique files
        size_dict = defaultdict(list)
        for f in files:
            try:
                size = os.path.getsize(f)
                size_dict[size].append(f)
            except OSError:
                continue

        # Step 2: Hash files that have the same size
        duplicates = defaultdict(list)
        for size, file_paths in size_dict.items():
            if len(file_paths) > 1:
                for file_path in file_paths:
                    file_hash = self._get_file_hash(file_path)
                    if file_hash:
                        duplicates[file_hash].append(file_path)

        # Filter out unique hashes
        return {h: paths for h, paths in duplicates.items() if len(paths) > 1}

    def _get_file_hash(self, filepath: str, chunk_size: int = 8192) -> str:
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError):
            return None
