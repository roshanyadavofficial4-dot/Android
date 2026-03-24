import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import wikipedia
except ImportError:
    wikipedia = None

class WikipediaAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("web.wikipedia.search", self.search_wikipedia)
        self.logger.info("Wikipedia Agent initialized. The sum of human knowledge, at your fingertips, Sir.")

    async def search_wikipedia(self, data: dict):
        query = data.get("query")
        sentences = data.get("sentences", 2)
        
        if not query:
            self.logger.error("Wikipedia search requested without a query.")
            return

        self.logger.info(f"Searching Wikipedia for: {query}")
        await self.event_bus.publish("speak", {"text": f"Consulting the archives for {query}, Sir."})
        
        if not wikipedia:
            self.logger.warning("wikipedia library not installed. Simulating Wikipedia search.")
            await self.event_bus.publish("speak", {"text": "I lack the wikipedia library to access the archives, Sir."})
            return

        summary = await asyncio.to_thread(self._search_sync, query, sentences)
        
        if summary:
            self.logger.info(f"Wikipedia search successful for: {query}")
            await self.event_bus.publish("speak", {"text": summary})
            await self.event_bus.publish("web.wikipedia.result", {"query": query, "summary": summary})
        else:
            self.logger.warning(f"No Wikipedia results found for: {query}")
            await self.event_bus.publish("speak", {"text": "I could find no mention of that in the archives, Sir."})

    def _search_sync(self, query: str, sentences: int) -> str:
        try:
            # Set language to English (default)
            wikipedia.set_lang("en")
            # Get the summary
            summary = wikipedia.summary(query, sentences=sentences)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            self.logger.warning(f"Disambiguation error for '{query}': {e.options}")
            return f"The term '{query}' is ambiguous. It could refer to {', '.join(e.options[:3])}, among other things."
        except wikipedia.exceptions.PageError:
            self.logger.warning(f"Page not found for '{query}'")
            return None
        except Exception as e:
            self.logger.error(f"Wikipedia search error: {e}")
            return None
