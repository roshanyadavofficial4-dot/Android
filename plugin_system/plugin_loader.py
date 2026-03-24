import os
import importlib.util
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class PluginLoader:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.plugin_dir = "plugins"
        
        os.makedirs(self.plugin_dir, exist_ok=True)
        self.logger.info("Plugin Loader initialized. Ready to accept foreign code, Sir.")

    async def load_plugins(self):
        self.logger.info(f"Scanning for plugins in {self.plugin_dir}...")
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                plugin_path = os.path.join(self.plugin_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, "setup"):
                            await module.setup(self.event_bus)
                            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
                        else:
                            self.logger.warning(f"Plugin {plugin_name} missing setup(event_bus) function.")
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
