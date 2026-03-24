import sqlite3
import os
from datetime import datetime, timedelta
from core.event_bus import EventBus
from core.logger import arya_logger

class HabitTracker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = "memory_system/user_memory.db"
        
        self._init_db()
        
        self.event_bus.subscribe("knowledge.habit.log", self.log_habit)
        self.event_bus.subscribe("knowledge.habit.report", self.generate_report)
        
        self.logger.info("Habit Tracker initialized. I shall monitor your biological and academic metrics, Sir.")

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_name TEXT,
                duration_hours REAL,
                log_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        # Table to track weak subjects based on study time or explicit user input
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weak_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT UNIQUE,
                struggle_level INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    async def log_habit(self, data: dict):
        habit_name = data.get("habit_name", "").lower() # e.g., "study", "sleep"
        duration = data.get("duration_hours", 0.0)
        subject = data.get("subject", None) # Optional, if habit is studying a specific subject
        
        if not habit_name or duration <= 0:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO habits (habit_name, duration_hours)
                VALUES (?, ?)
            ''', (habit_name, duration))
            
            # If studying a subject, maybe update weak subjects if duration is very high (indicating struggle)
            # or just log it for memory.
            if habit_name == "study" and subject:
                cursor.execute('''
                    INSERT INTO weak_subjects (subject, struggle_level) 
                    VALUES (?, 1) 
                    ON CONFLICT(subject) DO UPDATE SET struggle_level = struggle_level + 1
                ''', (subject.lower(),))
                
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged habit: {habit_name} for {duration} hours.")
            
            if habit_name == "study":
                await self.event_bus.publish("speak", {"text": f"Logged {duration} hours of studying. I'm sure your future patients will be grateful, Sir."})
            elif habit_name == "sleep":
                if duration < 5:
                    await self.event_bus.publish("speak", {"text": f"Only {duration} hours of sleep? Running on caffeine and sheer willpower is not a sustainable medical strategy, Sir."})
                else:
                    await self.event_bus.publish("speak", {"text": f"Logged {duration} hours of sleep. Adequate rest is crucial for memory consolidation."})
        except Exception as e:
            self.logger.error(f"Failed to log habit: {e}")

    async def generate_report(self, data: dict = None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get today's stats
            cursor.execute("SELECT habit_name, SUM(duration_hours) FROM habits WHERE log_date = CURRENT_DATE GROUP BY habit_name")
            today_stats = cursor.fetchall()
            
            # Get weak subjects
            cursor.execute("SELECT subject FROM weak_subjects ORDER BY struggle_level DESC LIMIT 3")
            weak_subjects = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            report = "Here is your daily biological and academic report, Sir. "
            for habit, duration in today_stats:
                report += f"You have logged {duration} hours of {habit}. "
                
            if weak_subjects:
                report += f"Based on your logs, you seem to be struggling with {', '.join(weak_subjects)}. I suggest focusing your efforts there."
                
            await self.event_bus.publish("speak", {"text": report})
        except Exception as e:
            self.logger.error(f"Failed to generate habit report: {e}")
