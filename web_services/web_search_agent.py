import asyncio
from duckduckgo_search import DDGS
from core.event_bus import EventBus
from core.logger import arya_logger

class WebSearchAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("web.search", self.search)
        self.logger.info("Web Search Agent online. The internet is at my disposal, Sir.")

    async def search(self, data: dict):
        query = data.get("query")
        if not query:
            self.logger.warning("Search requested but no query provided.")
            return

        self.logger.info(f"Searching the web for: {query}")
        await self.event_bus.publish("speak", {"text": "Searching the web, Sir. One moment."})
        
        def _perform_search():
            try:
                # Using DuckDuckGo Search (Free, No API Key required)
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=3))
                    return results
            except Exception as e:
                self.logger.error(f"Web search failed: {e}")
                return None

        results = await asyncio.to_thread(_perform_search)
        
        if results:
            # Compile a brief summary for the AI Brain to read or process
            summary = ""
            for res in results:
                summary += f"Title: {res.get('title')}\nSnippet: {res.get('body')}\n\n"
            
            self.logger.info("Search completed successfully.")
            await self.event_bus.publish("web.search.results", {
                "query": query, 
                "results": results, 
                "summary": summary
            })
            
            # Inform the user that data is ready for the Reasoning Engine
            await self.event_bus.publish("speak", {"text": "I have retrieved the information, Sir. Processing the data now."})
        else:
            await self.event_bus.publish("speak", {"text": "I'm afraid I couldn't find anything on that topic, Sir."})
