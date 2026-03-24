import asyncio
import urllib.request
import urllib.parse
import json
from core.event_bus import EventBus
from core.logger import arya_logger

class WeatherFetcher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.api_key = self._load_api_key()
        self.event_bus.subscribe("web.weather.fetch", self.fetch_weather)
        self.event_bus.subscribe("api_keys_updated", self._update_api_keys)
        self.logger.info("Weather Fetcher initialized. I'll let you know if you need an umbrella, Sir.")

    def _load_api_key(self):
        import json
        import os
        try:
            with open("core/data/secrets.json", "r") as f:
                secrets = json.load(f)
                return secrets.get("weather", os.environ.get("WEATHER_API_KEY", ""))
        except FileNotFoundError:
            return os.environ.get("WEATHER_API_KEY", "")

    async def _update_api_keys(self, payload: dict):
        weather_key = payload.get("weather")
        if weather_key:
            self.api_key = weather_key
            self.logger.info("Weather API Key updated in Weather Fetcher.")

    async def fetch_weather(self, data: dict):
        location = data.get("location", "")
        self.logger.info(f"Fetching weather for: {location if location else 'current location'}")
        
        def _get_weather():
            try:
                # Using wttr.in for a simple, no-API-key weather fetch
                # Format j1 returns JSON
                url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        return json.loads(response.read().decode())
            except Exception as e:
                self.logger.error(f"Weather fetch failed: {e}")
            return None

        weather_data = await asyncio.to_thread(_get_weather)
        
        if weather_data and "current_condition" in weather_data:
            current = weather_data["current_condition"][0]
            temp_c = current.get("temp_C")
            desc = current.get("weatherDesc")[0].get("value")
            
            msg = f"It is currently {temp_c} degrees Celsius and {desc}."
            if location:
                msg = f"In {location}, it is currently {temp_c} degrees Celsius and {desc}."
                
            await self.event_bus.publish("speak", {"text": msg})
            await self.event_bus.publish("web.weather.result", {"data": weather_data})
        else:
            await self.event_bus.publish("speak", {"text": "I couldn't retrieve the weather data, Sir. Look out a window."})
