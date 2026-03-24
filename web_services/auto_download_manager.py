import asyncio
import os
import urllib.parse
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import aiohttp
except ImportError:
    aiohttp = None

class AutoDownloadManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.download_dir = "/storage/emulated/0/Download/A.R.Y.A._Downloads"
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.event_bus.subscribe("web.download", self.handle_download)
        self.logger.info("Auto Download Manager initialized. I will fetch whatever digital artifacts you desire, Sir.")

    async def handle_download(self, data: dict):
        url = data.get("url")
        filename = data.get("filename")
        
        if not url:
            self.logger.error("Download requested without a URL.")
            return

        if not filename:
            # Extract filename from URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path) or "downloaded_file.pdf"
            
        save_path = os.path.join(self.download_dir, filename)
        
        self.logger.info(f"Starting download from {url} to {save_path}...")
        await self.event_bus.publish("speak", {"text": f"Downloading the requested file, Sir. Please hold."})
        
        if not aiohttp:
            self.logger.warning("aiohttp not installed. Cannot download file.")
            return

        success = await self._download_file(url, save_path)
        
        if success:
            self.logger.info(f"Download complete: {save_path}")
            await self.event_bus.publish("speak", {"text": f"Download complete, Sir. The file has been saved to your downloads folder as {filename}."})
            await self.event_bus.publish("web.download.complete", {"path": save_path})
        else:
            self.logger.error(f"Download failed for: {url}")
            await self.event_bus.publish("speak", {"text": "The download failed. The server is likely refusing my connection. How rude."})

    async def _download_file(self, url: str, save_path: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Write file asynchronously by offloading to a thread
                        # (Alternatively, use aiofiles if installed, but asyncio.to_thread is built-in and fine for this)
                        content = await response.read()
                        await asyncio.to_thread(self._write_file_sync, save_path, content)
                        return True
                    else:
                        self.logger.error(f"HTTP Error {response.status} while downloading {url}")
                        return False
        except Exception as e:
            self.logger.error(f"Download exception: {e}")
            return False

    def _write_file_sync(self, path: str, content: bytes):
        with open(path, 'wb') as f:
            f.write(content)
