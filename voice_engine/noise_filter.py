import speech_recognition as sr
import asyncio
from core.logger import arya_logger

class NoiseFilter:
    def __init__(self):
        self.logger = arya_logger
        self.logger.info("Noise Filter initialized. Attempting to ignore the dreadful background cacophony, Sir.")

    async def calibrate(self, recognizer: sr.Recognizer, source: sr.AudioSource, duration: float = 1.0):
        self.logger.debug(f"Async calibrating ambient noise for {duration} seconds...")
        await asyncio.to_thread(self.calibrate_sync, recognizer, source, duration)

    def calibrate_sync(self, recognizer: sr.Recognizer, source: sr.AudioSource, duration: float = 1.0):
        self.logger.debug("Sync calibrating ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=duration)
        self.logger.debug("Calibration complete. It's surprisingly noisy in here.")
