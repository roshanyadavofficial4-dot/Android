import os
import shutil
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class FileSorter:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.categories = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            "Documents": ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
            "Videos": ['.mp4', '.mkv', '.avi', '.mov'],
            "Audio": ['.mp3', '.wav', '.aac', '.flac'],
            "Archives": ['.zip', '.rar', '.tar', '.gz', '.7z'],
            "APKs": ['.apk']
        }
        
        self.event_bus.subscribe("file.sort_directory", self.handle_sort)
        self.logger.info("File Sorter initialized. I shall bring order to your chaotic directories, Sir.")

    async def handle_sort(self, data: dict):
        target_dir = data.get("path", "/storage/emulated/0/Download")
        await self.event_bus.publish("speak", {"text": f"Organizing the {os.path.basename(target_dir)} directory, Sir. It desperately needs it."})
        
        moved_count = await self.sort_directory(target_dir)
        
        if moved_count > 0:
            await self.event_bus.publish("speak", {"text": f"I have successfully categorized {moved_count} files. You're welcome."})
        else:
            await self.event_bus.publish("speak", {"text": "There was nothing to sort. How delightfully boring."})

    async def sort_directory(self, target_dir: str) -> int:
        return await asyncio.to_thread(self._sort_sync, target_dir)

    def _sort_sync(self, target_dir: str) -> int:
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            self.logger.error(f"Cannot sort {target_dir}: Directory does not exist.")
            return 0

        moved_count = 0
        try:
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                
                # Skip directories
                if os.path.isdir(item_path):
                    continue
                    
                _, ext = os.path.splitext(item)
                ext = ext.lower()
                
                # Find category
                target_category = "Others"
                for category, extensions in self.categories.items():
                    if ext in extensions:
                        target_category = category
                        break
                
                # Create category folder if it doesn't exist
                category_path = os.path.join(target_dir, target_category)
                if not os.path.exists(category_path):
                    os.makedirs(category_path)
                
                # Move file
                dest_path = os.path.join(category_path, item)
                # Avoid overwriting
                if not os.path.exists(dest_path):
                    shutil.move(item_path, dest_path)
                    moved_count += 1
                    self.logger.debug(f"Moved {item} to {target_category}")
                    
        except Exception as e:
            self.logger.error(f"Error sorting directory {target_dir}: {e}")
            
        return moved_count
