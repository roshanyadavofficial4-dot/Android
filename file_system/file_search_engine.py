import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from file_system.storage_scanner import StorageScanner

class FileSearchEngine:
    def __init__(self, event_bus: EventBus, scanner: StorageScanner):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.scanner = scanner
        
        self.event_bus.subscribe("file.search", self.handle_search)
        self.logger.info("File Search Engine initialized. I shall be your digital bloodhound, Sir.")

    async def handle_search(self, data: dict):
        query = data.get("query")
        if not query:
            self.logger.warning("Search requested without a query.")
            return

        self.logger.info(f"Searching for files matching: '{query}'")
        await self.event_bus.publish("speak", {"text": f"Searching your cluttered storage for {query}, Sir. This might take a moment."})
        
        results = await self.search(query)
        
        if results:
            self.logger.info(f"Found {len(results)} matches for '{query}'.")
            await self.event_bus.publish("speak", {"text": f"I have found {len(results)} files matching your query, Sir. I've logged their locations."})
            for res in results[:5]: # Log top 5
                self.logger.debug(f"Match found: {res}")
        else:
            self.logger.info(f"No matches found for '{query}'.")
            await self.event_bus.publish("speak", {"text": f"It appears '{query}' does not exist, Sir. Perhaps you deleted it in a fit of rage?"})

    async def search(self, query: str, path: str = None) -> list:
        # Get all files from the scanner
        all_files = await self.scanner.scan(path)
        
        # Filter files asynchronously
        results = await asyncio.to_thread(self._filter_files, all_files, query)
        return results

    def _filter_files(self, files: list, query: str) -> list:
        query_lower = query.lower()
        return [f for f in files if query_lower in os.path.basename(f).lower()]
