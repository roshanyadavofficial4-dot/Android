import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    from pyzbar.pyzbar import decode
    import cv2
    HAS_BARCODE = True
except ImportError:
    HAS_BARCODE = False

class BarcodeScanner:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("vision.barcode.scan", self.scan_barcode)
        if HAS_BARCODE:
            self.logger.info("Barcode Scanner initialized. Ready to read those little lines, Sir.")
        else:
            self.logger.warning("pyzbar/OpenCV not found. Barcode scanning is disabled, Sir.")

    async def scan_barcode(self, data: dict):
        image_path = data.get("image_path")
        if not image_path or not os.path.exists(image_path):
            self.logger.error("Invalid image path provided for barcode scanning.")
            return

        self.logger.info(f"Scanning for barcodes in {image_path}...")
        
        barcodes = await asyncio.to_thread(self._scan_sync, image_path)
        
        if barcodes:
            self.logger.debug(f"Found {len(barcodes)} barcodes.")
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                self.logger.info(f"Barcode: {barcode_data} (Type: {barcode_type})")
                await self.event_bus.publish("speak", {"text": f"I found a {barcode_type} barcode. The data is: {barcode_data}."})
        else:
            await self.event_bus.publish("speak", {"text": "I see no barcodes in this image, Sir."})

    def _scan_sync(self, image_path: str) -> list:
        try:
            image = cv2.imread(image_path)
            if image is None:
                return []
            return decode(image)
        except Exception as e:
            self.logger.error(f"Barcode scanning error: {e}")
            return []
