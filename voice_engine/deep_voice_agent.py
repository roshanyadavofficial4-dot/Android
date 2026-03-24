import asyncio
import os
import requests
from core.event_bus import EventBus
from core.logger import arya_logger

class DeepVoiceAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.voice_id = "21m00Tcm4TlvDq8ikWAM" # Default "Rachel" or user's cloned voice ID
        
        self.event_bus.subscribe("voice.deep.synthesize", self.synthesize_voice)
        self.event_bus.subscribe("voice.deep.call", self.make_ai_call)
        self.logger.info("Project Deep-Voice (ElevenLabs Integration) initialized. I can speak for you, Sir.")

    async def synthesize_voice(self, data: dict):
        text = data.get("text")
        if not text: return
        
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            self.logger.error("ELEVENLABS_API_KEY not found. Cannot use Deep-Voice.")
            await self.event_bus.publish("speak", {"text": "Sir, I require an ElevenLabs API key to use my advanced vocal synthesis."})
            return

        self.logger.info(f"Deep-Voice: Synthesizing high-quality audio for: {text}")
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            response = await asyncio.to_thread(requests.post, url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Save audio to temp file
                audio_path = "temp_deep_voice.mp3"
                with open(audio_path, "wb") as f:
                    f.write(response.content)
                
                self.logger.info("Deep-Voice: Audio synthesized successfully.")
                # Play the audio (using system player)
                await self.event_bus.publish("media.audio.play", {"file_path": audio_path})
            else:
                self.logger.error(f"ElevenLabs API error: {response.text}")
                await self.event_bus.publish("speak", {"text": "I'm having trouble connecting to the ElevenLabs servers, Sir."})

        except Exception as e:
            self.logger.error(f"Deep-Voice synthesis failed: {e}")

    async def make_ai_call(self, data: dict):
        recipient = data.get("recipient")
        purpose = data.get("purpose")
        
        self.logger.info(f"Deep-Voice: Initiating AI call to {recipient} for {purpose}")
        await self.event_bus.publish("speak", {"text": f"Initiating the Deep-Voice call protocol for {recipient}, Sir. I'll handle the conversation."})
        
        # In a real Android app, we'd use Twilio or a similar service to bridge the call
        # For this prototype, we simulate the intent
        try:
            # 1. Generate the script via Gemini
            script_prompt = f"Generate a short, professional phone script for an AI assistant calling {recipient} to {purpose}. The assistant's name is A.R.Y.A."
            # (Logic to call Gemini would go here)
            
            # 2. Trigger Android Dialer (via pyjnius)
            # This just opens the dialer with the number
            await self.event_bus.publish("controller.system.call", {"number": recipient})
            
            self.logger.info("Deep-Voice: Call intent triggered.")
        except Exception as e:
            self.logger.error(f"Deep-Voice call failed: {e}")
