import asyncio
import xml.etree.ElementTree as ET
import urllib.parse
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import aiohttp
except ImportError:
    aiohttp = None

class NewsFetcher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("web.news.fetch", self.handle_fetch_news)
        self.logger.info("News Fetcher initialized. Ready to depress you with current events, Sir.")

    async def handle_fetch_news(self, data: dict):
        category = data.get("category", "general").lower()
        
        self.logger.info(f"Fetching news for category: {category}")
        await self.event_bus.publish("speak", {"text": f"Retrieving the latest {category} updates, Sir. Brace yourself."})
        
        if not aiohttp:
            self.logger.warning("aiohttp not installed. Cannot fetch news.")
            return

        if category in ["medical", "pubmed", "health"]:
            articles = await self._fetch_pubmed_rss()
        else:
            articles = await self._fetch_general_news()
            
        if articles:
            top_articles = articles[:3]
            news_text = " Here are the top headlines. "
            for i, article in enumerate(top_articles):
                news_text += f"{i+1}: {article['title']}. "
                
            await self.event_bus.publish("speak", {"text": news_text})
            await self.event_bus.publish("web.news.result", {"category": category, "articles": articles})
        else:
            await self.event_bus.publish("speak", {"text": "I couldn't find any news. Perhaps the world has finally ended, Sir."})

    async def _fetch_pubmed_rss(self) -> list:
        # Fetching latest medical articles from PubMed via RSS
        # Using a generic search term 'medicine' or 'latest'
        url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1-P2r_wY1bN_kP6c83V_m8J_/" # Example RSS feed structure
        # A more reliable public RSS for medical news:
        url = "https://medicalxpress.com/rss-feed/"
        
        articles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        root = ET.fromstring(xml_data)
                        for item in root.findall('.//item'):
                            title = item.find('title').text if item.find('title') is not None else "No Title"
                            link = item.find('link').text if item.find('link') is not None else ""
                            articles.append({"title": title, "link": link})
                            if len(articles) >= 5:
                                break
        except Exception as e:
            self.logger.error(f"PubMed/Medical RSS fetch error: {e}")
            
        return articles

    async def _fetch_general_news(self) -> list:
        # Using BBC News RSS as a reliable general news source
        url = "http://feeds.bbci.co.uk/news/rss.xml"
        articles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        root = ET.fromstring(xml_data)
                        for item in root.findall('.//item'):
                            title = item.find('title').text if item.find('title') is not None else "No Title"
                            link = item.find('link').text if item.find('link') is not None else ""
                            articles.append({"title": title, "link": link})
                            if len(articles) >= 5:
                                break
        except Exception as e:
            self.logger.error(f"General news fetch error: {e}")
            
        return articles
