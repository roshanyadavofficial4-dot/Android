import asyncio
import sqlite3
import os
from core.event_bus import EventBus
from core.logger import arya_logger

class PreferenceStore:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = os.path.join(os.path.dirname(__file__), "user_memory.db")
        self._init_db()
        
        self.event_bus.subscribe("preference.set", self.set_preference)
        self.event_bus.subscribe("preference.get", self.get_preference)
        self.logger.info("Preference Store initialized. I know what you like, Sir.")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()
        conn.close()

    async def set_preference(self, data: dict):
        key = data.get("key")
        value = data.get("value")
        if not key: return
        
        def _insert():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO preferences (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            conn.commit()
            conn.close()
            
        await asyncio.to_thread(_insert)
        self.logger.debug(f"Preference saved: {key} = {value}")
        await self.event_bus.publish(f"preference.updated.{key}", {"key": key, "value": value})
        await self.event_bus.publish("preference.updated", {"key": key, "value": value})

    async def get_preference(self, data: dict):
        key = data.get("key")
        if not key: return
        
        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
            
        value = await asyncio.to_thread(_fetch)
        await self.event_bus.publish(f"preference.result.{key}", {"key": key, "value": value})
