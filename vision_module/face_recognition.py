import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import face_recognition
    import cv2
    HAS_FACE = True
except ImportError:
    HAS_FACE = False

class FaceRecognitionEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Load the Creator's face encoding (In production, this would be loaded from secure_storage)
        self.creator_name = "The Creator"
        self.creator_encoding = None 
        
        self.event_bus.subscribe("vision.face.recognize", self.handle_recognition)
        if HAS_FACE:
            self.logger.info("Face Recognition Engine initialized. I shall try to remember your face, Sir.")
        else:
            self.logger.warning("face_recognition/OpenCV not found. Face recognition is disabled, Sir.")

    async def handle_recognition(self, data: dict):
        image_path = data.get("image_path")
        if not image_path or not os.path.exists(image_path):
            self.logger.error("Invalid image path provided for face recognition.")
            return

        self.logger.info(f"Analyzing faces in {image_path}...")
        
        names = await asyncio.to_thread(self._recognize_sync, image_path)
        
        if self.creator_name in names:
            await self.event_bus.publish("speak", {"text": "Good to see you, Sir. You're looking exceptionally well today."})
        elif names:
            await self.event_bus.publish("speak", {"text": f"I detect an unknown entity. Identify yourself, before I trigger the alarms."})
        else:
            await self.event_bus.publish("speak", {"text": "I see no faces here. Just the void."})

    def _recognize_sync(self, image_path: str) -> list:
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            detected_names = []
            for face_encoding in face_encodings:
                # If we had a creator encoding, we would compare it here:
                # matches = face_recognition.compare_faces([self.creator_encoding], face_encoding)
                # For now, we simulate finding the creator if any face is found
                detected_names.append(self.creator_name)
                
            return detected_names
        except Exception as e:
            self.logger.error(f"Face recognition error: {e}")
            return []
