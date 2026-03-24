import asyncio
import urllib.request
import json
from core.event_bus import EventBus
from core.logger import arya_logger

class StockTracker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("web.stock.fetch", self.fetch_stock)
        self.logger.info("Stock Tracker initialized. Ready to monitor your portfolio, Sir.")

    async def fetch_stock(self, data: dict):
        symbol = data.get("symbol")
        if not symbol:
            self.logger.error("Stock fetch requested without a symbol.")
            return

        symbol = symbol.upper()
        self.logger.info(f"Fetching stock price for: {symbol}")
        await self.event_bus.publish("speak", {"text": f"Checking the market for {symbol}, Sir."})
        
        stock_data = await asyncio.to_thread(self._fetch_sync, symbol)
        
        if stock_data:
            price = stock_data.get("price")
            change = stock_data.get("change")
            change_percent = stock_data.get("change_percent")
            
            direction = "up" if float(change) >= 0 else "down"
            
            msg = f"{symbol} is currently trading at {price}, {direction} {abs(float(change))} points, or {change_percent}."
            self.logger.info(f"Stock data fetched: {msg}")
            await self.event_bus.publish("speak", {"text": msg})
            await self.event_bus.publish("web.stock.result", {"symbol": symbol, "data": stock_data})
        else:
            self.logger.warning(f"Could not fetch stock data for: {symbol}")
            await self.event_bus.publish("speak", {"text": f"I could not retrieve the current price for {symbol}, Sir. The market might be closed, or the symbol is invalid."})

    def _fetch_sync(self, symbol: str) -> dict:
        try:
            # Using Yahoo Finance API (v8)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    result = data.get("chart", {}).get("result", [])
                    if result:
                        meta = result[0].get("meta", {})
                        regularMarketPrice = meta.get("regularMarketPrice")
                        previousClose = meta.get("previousClose")
                        
                        if regularMarketPrice is not None and previousClose is not None:
                            change = regularMarketPrice - previousClose
                            change_percent = (change / previousClose) * 100
                            
                            return {
                                "price": round(regularMarketPrice, 2),
                                "change": round(change, 2),
                                "change_percent": f"{round(change_percent, 2)}%"
                            }
            return None
        except Exception as e:
            self.logger.error(f"Stock fetch error for {symbol}: {e}")
            return None
