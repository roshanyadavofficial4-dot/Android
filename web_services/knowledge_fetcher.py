import asyncio
import urllib.parse
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import aiohttp
except ImportError:
    aiohttp = None

class KnowledgeFetcher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.wolfram_app_id = os.getenv("WOLFRAM_APP_ID", "")
        
        self.event_bus.subscribe("web.knowledge.query", self.handle_query)
        self.logger.info("Knowledge Fetcher initialized. Ready to answer your trivial questions, Sir.")

    async def handle_query(self, data: dict):
        query = data.get("query")
        source = data.get("source", "wikipedia").lower() # 'wikipedia' or 'wolfram'
        
        if not query:
            return

        self.logger.info(f"Knowledge query: '{query}' via {source}")
        
        if not aiohttp:
            self.logger.warning("aiohttp not installed. Cannot fetch knowledge.")
            return

        if source == "wolfram" and self.wolfram_app_id:
            answer = await self._query_wolfram(query)
        else:
            answer = await self._query_wikipedia(query)
            
        if answer:
            self.logger.info(f"Knowledge retrieved: {answer[:100]}...")
            await self.event_bus.publish("speak", {"text": answer})
            await self.event_bus.publish("web.knowledge.result", {"query": query, "answer": answer})
        else:
            await self.event_bus.publish("speak", {"text": "I could not find a definitive answer to that, Sir. Perhaps it is a mystery best left unsolved."})

    async def _query_wikipedia(self, query: str) -> str:
        # Wikipedia Summary API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        extract = data.get("extract")
                        if extract:
                            return extract
                    elif response.status == 404:
                        # Try a standard search if exact match fails
                        return await self._search_wikipedia(query)
        except Exception as e:
            self.logger.error(f"Wikipedia API error: {e}")
        return None

    async def _search_wikipedia(self, query: str) -> str:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        search_results = data.get("query", {}).get("search", [])
                        if search_results:
                            snippet = search_results[0].get("snippet", "")
                            # Clean HTML tags from snippet
                            import re
                            clean_snippet = re.sub('<[^<]+>', '', snippet)
                            return f"According to Wikipedia: {clean_snippet}..."
        except Exception as e:
            self.logger.error(f"Wikipedia Search error: {e}")
        return None

    async def _query_wolfram(self, query: str) -> str:
        # Wolfram Short Answer API
        url = f"http://api.wolframalpha.com/v1/result?appid={self.wolfram_app_id}&i={urllib.parse.quote(query)}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        answer = await response.text()
                        return answer
                    else:
                        self.logger.error(f"Wolfram API error: {response.status}")
        except Exception as e:
            self.logger.error(f"Wolfram API exception: {e}")
        return None
