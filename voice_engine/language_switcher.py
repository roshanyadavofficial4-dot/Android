from core.event_bus import EventBus
from core.logger import arya_logger

class LanguageSwitcher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.current_language = "en-GB" # Default to British English
        self.supported_languages = {
            "english": "en-GB",
            "hindi": "hi-IN"
        }
        self.event_bus.subscribe("switch_language", self.switch_language)
        self.logger.info("Language Switcher initialized. Polyglot mode engaged, Sir.")

    async def switch_language(self, data: dict):
        lang = data.get("language", "").lower()
        if lang in self.supported_languages:
            self.current_language = self.supported_languages[lang]
            self.logger.info(f"Language switched to {self.current_language}.")
            
            response = "Language switched to English, Sir." if lang == "english" else "भाषा बदल दी गई है, सर।"
            await self.event_bus.publish("speak", {"text": response})
        else:
            self.logger.warning(f"Attempted to switch to unsupported language: {lang}")
            await self.event_bus.publish("speak", {"text": "I'm afraid I don't speak that language yet, Sir. I shall stick to what I know."})

    def get_current_language(self) -> str:
        return self.current_language
