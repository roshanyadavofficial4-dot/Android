import asyncio
import sqlite3
import os
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger

class HistoryTracker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = os.path.join(os.path.dirname(__file__), "user_memory.db")
        self._init_db()
        
        self.event_bus.subscribe("command.executed", self.log_command)
        self.logger.info("History Tracker initialized. I remember everything, Sir.")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                command TEXT,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    async def log_command(self, data: dict):
        command = data.get("command", "")
        status = data.get("status", "success")
        
        def _insert():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO command_history (timestamp, command, status) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), command, status)
            )
            conn.commit()
            conn.close()
            
        await asyncio.to_thread(_insert)
        self.logger.debug(f"Logged command to history: {command}")
