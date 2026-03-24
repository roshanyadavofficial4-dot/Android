import sqlite3
import asyncio
import os
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger

class ReminderEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = "memory_system/user_memory.db"
        
        self._init_db()
        
        self.event_bus.subscribe("knowledge.reminder.add", self.add_reminder)
        self.event_bus.subscribe("knowledge.reminder.list", self.list_reminders)
        
        self.logger.info("Reminder Engine initialized. I shall attempt to keep your chaotic schedule on track, Sir.")
        
        # Start the background checker
        asyncio.create_task(self._check_reminders_loop())

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                message TEXT,
                remind_time DATETIME,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()
        conn.close()

    async def add_reminder(self, data: dict):
        remind_type = data.get("type", "general") # medicine, class, exam, general
        message = data.get("message")
        remind_time_str = data.get("time") # Expected format: YYYY-MM-DD HH:MM:SS
        
        if not message or not remind_time_str:
            self.logger.error("Cannot add reminder without message and time.")
            return

        try:
            # Validate time format
            datetime.strptime(remind_time_str, "%Y-%m-%d %H:%M:%S")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (type, message, remind_time)
                VALUES (?, ?, ?)
            ''', (remind_type, message, remind_time_str))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Reminder added: {message} at {remind_time_str}")
            await self.event_bus.publish("speak", {"text": f"Reminder set for {remind_time_str}, Sir. Try not to ignore it when the time comes."})
        except Exception as e:
            self.logger.error(f"Failed to add reminder: {e}")

    async def list_reminders(self, data: dict = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT type, message, remind_time FROM reminders WHERE status = 'pending' ORDER BY remind_time ASC LIMIT 5")
        reminders = cursor.fetchall()
        conn.close()
        
        if reminders:
            response = "Your upcoming impending dooms are as follows: "
            for r in reminders:
                response += f"A {r[0]} reminder to {r[1]} at {r[2]}. "
            await self.event_bus.publish("speak", {"text": response})
        else:
            await self.event_bus.publish("speak", {"text": "You have no pending reminders. A rare moment of peace, Sir."})

    async def _check_reminders_loop(self):
        while True:
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Find due reminders
                cursor.execute("SELECT id, type, message FROM reminders WHERE status = 'pending' AND remind_time <= ?", (now,))
                due_reminders = cursor.fetchall()
                
                for r_id, r_type, message in due_reminders:
                    self.logger.info(f"Reminder triggered: {message}")
                    
                    # Announce the reminder
                    announcement = f"Sir, a {r_type} reminder requires your attention: {message}."
                    if r_type == "medicine":
                        announcement = f"Sir, it is time for your medication: {message}. Please don't make me remind you again."
                    elif r_type == "exam":
                        announcement = f"Sir, impending academic doom approaches. Exam reminder: {message}."
                        
                    await self.event_bus.publish("speak", {"text": announcement})
                    
                    # Mark as completed
                    cursor.execute("UPDATE reminders SET status = 'completed' WHERE id = ?", (r_id,))
                
                conn.commit()
                conn.close()
            except Exception as e:
                self.logger.error(f"Error in reminder loop: {e}")
                
            await asyncio.sleep(30) # Check every 30 seconds
