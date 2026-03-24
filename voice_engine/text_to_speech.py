import asyncio
import os
import subprocess
from gtts import gTTS
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID, IS_PC

if IS_PC:
    try:
        import playsound
    except ImportError:
        playsound = None

class TextToSpeech:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("speak", self.speak)
        self.logger.info("Text-to-Speech engine online. I have found my voice, Sir.")

    async def speak(self, data: dict):
        text = data.get("text", "")
        if not text:
            return
        
        self.logger.info(f"A.R.Y.A.: {text}")
        
        def _generate_and_play():
            try:
                # Detect Hindi characters to switch voice dynamically
                is_hindi = any('\u0900' <= c <= '\u097F' for c in text)
                # Use Microsoft Edge TTS for highly realistic, human-like voices
                # en-GB-RyanNeural is a sophisticated British male voice (Jarvis-like)
                # hi-IN-MadhurNeural is a high-quality Hindi male voice
                voice = "hi-IN-MadhurNeural" if is_hindi else "en-GB-RyanNeural"
                
                if IS_ANDROID:
                    filepath = "/tmp/arya_speech.mp3"
                    if not os.path.exists("/tmp"):
                        filepath = os.path.expanduser("~/arya_speech.mp3")
                else:
                    import tempfile
                    filepath = os.path.join(tempfile.gettempdir(), "arya_speech.mp3")
                
                # Use edge-tts CLI tool
                cmd = f"edge-tts --voice {voice} --text \"{text}\" --write-media {filepath}"
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Play audio dynamically based on platform
                if IS_ANDROID:
                    os.system(f"termux-media-player play {filepath} > /dev/null 2>&1")
                elif IS_PC:
                    if playsound:
                        try:
                            playsound.playsound(filepath)
                        except Exception as e:
                            self.logger.error(f"PC audio player choked: {e}")
                    else:
                        # Fallback OS commands
                        import platform
                        sys_name = platform.system()
                        if sys_name == 'Windows':
                            os.system(f"start {filepath}")
                        elif sys_name == 'Darwin':
                            subprocess.run(["afplay", filepath], check=True)
                        else:
                            subprocess.run(["mpg123", filepath], check=True)
            except Exception as e:
                self.logger.error(f"edge-tts Error: {e}. Attempting offline fallback.")
                # Fallback to pyttsx3 if offline or edge-tts fails
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    # Try to set a British/English voice if available
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if 'english' in voice.name.lower() or 'uk' in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            break
                    engine.say(text)
                    engine.runAndWait()
                except Exception as fallback_e:
                    self.logger.error(f"TTS Fallback Error: {fallback_e}")

        await asyncio.to_thread(_generate_and_play)
