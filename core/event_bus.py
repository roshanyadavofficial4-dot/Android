import asyncio
from typing import Callable, Dict, List, Any
from core.logger import arya_logger

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.logger = arya_logger
        self.logger.info("Event Bus initialized. Ready to route your demands, Sir.")

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"New subscriber for event: {event_type}. How thrilling.")

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Subscriber removed for event: {event_type}. Good riddance.")

    async def publish(self, event_type: str, data: Any = None):
        self.logger.debug(f"Publishing event: {event_type} with data: {data}")
        if event_type in self.subscribers:
            callbacks = self.subscribers[event_type]
            tasks = []
            for callback in callbacks:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(asyncio.create_task(callback(data)))
                else:
                    # Run synchronous callbacks in a thread pool to avoid blocking
                    tasks.append(asyncio.to_thread(callback, data))
            
            if tasks:
                await asyncio.gather(*tasks)
        else:
            self.logger.warning(f"Event {event_type} published, but alas, no one is listening. Story of my life.")
