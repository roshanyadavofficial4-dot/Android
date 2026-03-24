import asyncio
import os
import speech_recognition as sr
from core.event_bus import EventBus
from core.logger import arya_logger

class SpeechToText:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.recognizer = sr.Recognizer()
        
        self.event_bus.subscribe("listen_for_command", self.listen)
        self.logger.info("Speech-to-Text engine (Google Web API) online. I am listening, Sir.")

    async def listen(self, data: dict = None):
        def _capture_and_recognize():
            with sr.Microphone() as source:
                self.logger.info("Listening for command...")
                # Subtle haptic feedback to indicate listening state on Android
                os.system("termux-vibrate -d 50 > /dev/null 2>&1")
                
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.WaitTimeoutError:
                    self.logger.warning("Listening timed out.")
                    return ""
                except sr.UnknownValueError:
                    self.logger.warning("Google Speech Recognition could not understand audio.")
                    return ""
                except sr.RequestError as e:
                    self.logger.error(f"Could not request results from Google Speech Recognition service; {e}")
                    return ""
                except Exception as e:
                    self.logger.error(f"STT Error: {e}")
                    return ""

        text = await asyncio.to_thread(_capture_and_recognize)
        
        if text:
            self.logger.info(f"User said: {text}")
            await self.event_bus.publish("command_received", {"command": text})
        else:
            await self.event_bus.publish("speak", {"text": "I didn't quite catch that, Sir."})
