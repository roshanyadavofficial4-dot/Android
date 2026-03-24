import asyncio
import time
from typing import Dict, Any
from core.event_bus import EventBus
from core.logger import arya_logger

class TaskScheduler:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.tasks: Dict[str, asyncio.Task] = {}
        self.event_bus.subscribe("schedule_task", self.schedule_task)
        self.event_bus.subscribe("cancel_task", self.cancel_task)
        self.logger.info("Task Scheduler initialized. I shall keep track of time, since you clearly cannot, Sir.")

    async def schedule_task(self, data: dict):
        task_id = data.get("task_id", f"task_{int(time.time())}")
        delay = data.get("delay", 0)  # in seconds
        event_to_publish = data.get("event")
        payload = data.get("payload", {})
        
        if not event_to_publish:
            self.logger.error("Cannot schedule a task without an event to publish.")
            return

        self.logger.info(f"Scheduling task '{task_id}' to execute in {delay} seconds.")
        
        task = asyncio.create_task(self._delayed_execution(task_id, delay, event_to_publish, payload))
        self.tasks[task_id] = task

    async def _delayed_execution(self, task_id: str, delay: int, event: str, payload: Any):
        try:
            await asyncio.sleep(delay)
            self.logger.info(f"Executing scheduled task: {task_id}")
            await self.event_bus.publish(event, payload)
        except asyncio.CancelledError:
            self.logger.info(f"Task {task_id} was cancelled. I suppose we didn't need to do that after all.")
        finally:
            if task_id in self.tasks:
                del self.tasks[task_id]

    async def cancel_task(self, data: dict):
        task_id = data.get("task_id")
        if task_id and task_id in self.tasks:
            self.tasks[task_id].cancel()
            self.logger.info(f"Cancelled task: {task_id}")
        else:
            self.logger.warning(f"Attempted to cancel non-existent task: {task_id}")
