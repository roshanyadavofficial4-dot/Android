from core.event_bus import EventBus
from core.logger import arya_logger
from plugin_system.plugin_loader import PluginLoader

class PluginManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.loader = PluginLoader(event_bus)
        
        self.event_bus.subscribe("system.plugins.reload", self.reload_plugins)
        self.logger.info("Plugin Manager initialized. Overseeing the extensions, Sir.")

    async def initialize(self):
        await self.loader.load_plugins()

    async def reload_plugins(self, data: dict = None):
        self.logger.info("Reloading plugins...")
        await self.event_bus.publish("speak", {"text": "Reloading plugins, Sir. Let's hope none of them crash the system."})
        await self.loader.load_plugins()
        await self.event_bus.publish("speak", {"text": "Plugins reloaded successfully."})
