import sqlite3
import os
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger

class NoteManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = "memory_system/user_memory.db"
        
        self._init_db()
        
        self.event_bus.subscribe("knowledge.note.save", self.save_note)
        self.event_bus.subscribe("knowledge.note.search", self.search_notes)
        
        self.logger.info("Note Manager initialized. I am ready to transcribe your medical musings, Sir.")

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                tags TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    async def save_note(self, data: dict):
        title = data.get("title", "Untitled Clinical Note")
        content = data.get("content")
        tags = data.get("tags", "general") # e.g., "anatomy, rounds, patient"
        
        if not content:
            self.logger.warning("Attempted to save an empty note.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (title, content, tags)
                VALUES (?, ?, ?)
            ''', (title, content, tags))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Note saved: {title}")
            await self.event_bus.publish("speak", {"text": f"I have saved your note on {title}, Sir. I sincerely hope you can read it later."})
        except Exception as e:
            self.logger.error(f"Failed to save note: {e}")
            await self.event_bus.publish("speak", {"text": "There was an error saving your note. The knowledge is lost to the ether."})

    async def search_notes(self, data: dict):
        query = data.get("query", "").lower()
        
        if not query:
            return

        self.logger.info(f"Searching notes for: {query}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Simple LIKE search. In a full RAG system, this would be semantic.
            cursor.execute('''
                SELECT title, content FROM notes 
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY timestamp DESC LIMIT 3
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            
            if results:
                await self.event_bus.publish("speak", {"text": f"I found {len(results)} relevant notes, Sir."})
                for title, content in results:
                    self.logger.info(f"Note Found - {title}: {content[:100]}...")
            else:
                await self.event_bus.publish("speak", {"text": f"I found no notes matching '{query}'. Perhaps you slept through that lecture, Sir."})
        except Exception as e:
            self.logger.error(f"Failed to search notes: {e}")
