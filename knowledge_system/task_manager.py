import asyncio
import sqlite3
import os
from core.event_bus import EventBus
from core.logger import arya_logger

class TaskManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.db_path = os.path.join(os.environ.get("HOME", "."), "tasks.db")
        self._init_db()
        
        self.event_bus.subscribe("task.add", self.add_task)
        self.event_bus.subscribe("task.list", self.list_tasks)
        self.event_bus.subscribe("task.complete", self.complete_task)
        self.logger.info("Task Manager initialized. Let's get things done, Sir.")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()
        conn.close()

    async def add_task(self, data: dict):
        task = data.get("task")
        if not task: return

        def _insert():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_insert)
        self.logger.info(f"Task added: {task}")
        await self.event_bus.publish("speak", {"text": f"Task added to your list, Sir: {task}"})

    async def list_tasks(self, data: dict):
        def _fetch():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, task FROM tasks WHERE status = 'pending'")
            rows = cursor.fetchall()
            conn.close()
            return rows

        tasks = await asyncio.to_thread(_fetch)
        
        if tasks:
            msg = f"You have {len(tasks)} pending tasks. "
            for _, task in tasks:
                msg += f"{task}. "
            await self.event_bus.publish("speak", {"text": msg})
        else:
            await self.event_bus.publish("speak", {"text": "You have no pending tasks, Sir. Enjoy your free time."})

    async def complete_task(self, data: dict):
        task_id = data.get("task_id")
        if not task_id: return

        def _update():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_update)
        self.logger.info(f"Task {task_id} marked as completed.")
        await self.event_bus.publish("speak", {"text": "Task marked as completed, Sir. Excellent work."})
