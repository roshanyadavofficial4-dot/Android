# To download the required Vosk model, run the following commands in your terminal:
# wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
# unzip vosk-model-small-en-us-0.15.zip
# mv vosk-model-small-en-us-0.15 model

import asyncio
import json
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import vosk
    import pyaudio
except ImportError:
    vosk = None
    pyaudio = None

class WakeWordEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.wake_words = ["arya", "aria", "are ya", "jarvis"]
        self.is_listening = False
        self.model_path = "model"
        
        self.model = None
        self.recognizer = None
        self.p = None
        self.stream = None
        
        self.event_bus.subscribe("preference.updated.wake_words", self.update_wake_words)
        # Request current wake words on init
        asyncio.create_task(self._request_initial_wake_words())
        
        self.logger.info("Wake Word Engine initialized. I am always listening, Sir... in a non-creepy way.")

    async def _request_initial_wake_words(self):
        # Wait a bit for PreferenceStore to be ready
        await asyncio.sleep(2)
        self.event_bus.subscribe("preference.result.wake_words", self.update_wake_words)
        await self.event_bus.publish("preference.get", {"key": "wake_words"})

    async def update_wake_words(self, data: dict):
        value = data.get("value")
        if value:
            # Value is a comma-separated string
            new_words = [w.strip().lower() for w in value.split(",")]
            if new_words:
                self.wake_words = new_words
                self.logger.info(f"Wake words updated: {self.wake_words}")

    async def start(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.logger.info("Wake word listener started.")
        asyncio.create_task(self._listen_loop())

    async def stop(self):
        self.is_listening = False
        self.logger.info("Wake word listener stopped. Enjoy the silence, Sir.")

    async def _listen_loop(self):
        if not vosk or not pyaudio:
            self.logger.error("Vosk or PyAudio not installed. Cannot start wake word engine.")
            self.is_listening = False
            return
            
        if not os.path.exists(self.model_path):
            self.logger.error(f"Vosk model not found at '{self.model_path}'. Please download it.")
            self.is_listening = False
            return
            
        self.model = vosk.Model(self.model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
        self.stream.start_stream()
        
        while self.is_listening:
            audio_data = await asyncio.to_thread(self._capture_audio_chunk)
            if audio_data:
                await self._process_wake_word(audio_data)
                
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def _capture_audio_chunk(self):
        try:
            data = self.stream.read(4000, exception_on_overflow=False)
            return data
        except Exception as e:
            self.logger.error(f"Microphone error in wake word engine: {e}")
            return None

    async def _process_wake_word(self, audio):
        try:
            if self.recognizer.AcceptWaveform(audio):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower()
                
                if any(word in text for word in self.wake_words):
                    self.logger.info(f"Wake word detected in text: '{text}'")
                    await self.event_bus.publish("speak", {"text": "At your service, Sir."})
                    # Trigger the main STT engine to listen for the actual command
                    await self.event_bus.publish("listen_for_command", {})
        except Exception as e:
            self.logger.error(f"Wake word recognition error: {e}")
