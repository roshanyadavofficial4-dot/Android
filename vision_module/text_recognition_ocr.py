import asyncio
from PIL import Image
import re
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class TextRecognitionOCR:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Medical abbreviations dictionary for the MBBS student
        self.medical_abbreviations = {
            r'\bbid\b': 'Bis in die (Twice a day)',
            r'\btid\b': 'Ter in die (Three times a day)',
            r'\bod\b': 'Omne in die (Once a day)',
            r'\bqid\b': 'Quater in die (Four times a day)',
            r'\bhs\b': 'Hora somni (At bedtime)',
            r'\bprn\b': 'Pro re nata (As needed)',
            r'\bstat\b': 'Statim (Immediately)',
            r'\bpo\b': 'Per os (By mouth)',
            r'\biv\b': 'Intravenous',
            r'\bim\b': 'Intramuscular',
            r'\brx\b': 'Prescription',
            r'\bhx\b': 'History',
            r'\bdx\b': 'Diagnosis',
            r'\btx\b': 'Treatment',
            r'\bc/o\b': 'Complains of',
            r'\bo/e\b': 'On examination'
        }
        
        self.event_bus.subscribe("vision.ocr.read", self.handle_ocr)
        if HAS_OCR:
            self.logger.info("OCR Engine initialized. Ready to decipher doctors' handwriting, Sir. May God help us all.")
        else:
            self.logger.warning("pytesseract not found. OCR is disabled, Sir.")

    async def handle_ocr(self, data: dict):
        image_path = data.get("image_path")
        if not image_path:
            return

        self.logger.info(f"Running OCR on {image_path}...")
        await self.event_bus.publish("speak", {"text": "Scanning the document, Sir. Let's see what hieroglyphics we have today."})
        
        extracted_text = await asyncio.to_thread(self._extract_text_sync, image_path)
        
        if extracted_text:
            parsed_text = self._parse_medical_abbreviations(extracted_text)
            self.logger.debug(f"Extracted Text: {parsed_text}")
            
            # Send the parsed text back to the AI engine or read it out loud
            await self.event_bus.publish("speak", {"text": "I have transcribed the text. I've also expanded the medical abbreviations for your convenience, Doctor."})
            await self.event_bus.publish("vision.ocr.result", {"raw_text": extracted_text, "parsed_text": parsed_text})
        else:
            await self.event_bus.publish("speak", {"text": "I couldn't extract any readable text. Either the image is blurry, or the handwriting is truly terminal."})

    def _extract_text_sync(self, image_path: str) -> str:
        try:
            # For handwritten medical notes, psm 6 or 3 is usually preferred
            custom_config = r'--oem 3 --psm 6'
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, config=custom_config)
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR Error: {e}")
            return ""

    def _parse_medical_abbreviations(self, text: str) -> str:
        """
        Scans the text for common medical abbreviations and appends their meanings.
        """
        parsed_text = text
        found_abbreviations = []
        
        for pattern, meaning in self.medical_abbreviations.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_abbreviations.append(f"{pattern.replace(r'\b', '')} -> {meaning}")
                
        if found_abbreviations:
            parsed_text += "\n\n--- A.R.Y.A. Medical Analysis ---\n"
            parsed_text += "Abbreviations Detected:\n" + "\n".join(found_abbreviations)
            
        return parsed_text
