import asyncio
import sqlite3
import os
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger

class CalendarManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = os.path.join(os.path.dirname(__file__), "calendar.db")
        self._init_db()
        
        self.event_bus.subscribe("calendar.add", self.add_event)
        self.event_bus.subscribe("calendar.get", self.get_events)
        self.logger.info("Calendar Manager initialized. Your schedule is in my hands, Sir.")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                date TEXT,
                time TEXT
            )
        ''')
        conn.commit()
        conn.close()

    async def add_event(self, data: dict):
        title = data.get("title")
        date = data.get("date")
        time = data.get("time", "")
        
        if not title or not date:
            self.logger.warning("Cannot add event without title and date.")
            return

        def _insert():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (title, date, time) VALUES (?, ?, ?)", (title, date, time))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_insert)
        self.logger.info(f"Event added: {title} on {date} at {time}")
        await self.event_bus.publish("speak", {"text": f"I have added {title} to your calendar for {date}, Sir."})

    async def get_events(self, data: dict):
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT title, time FROM events WHERE date = ?", (date,))
            rows = cursor.fetchall()
            conn.close()
            return rows

        events = await asyncio.to_thread(_fetch)
        
        if events:
            msg = f"You have {len(events)} events scheduled for {date}. "
            for title, time in events:
                msg += f"{title} at {time if time else 'any time'}. "
            await self.event_bus.publish("speak", {"text": msg})
        else:
            await self.event_bus.publish("speak", {"text": f"Your schedule is clear for {date}, Sir."})
