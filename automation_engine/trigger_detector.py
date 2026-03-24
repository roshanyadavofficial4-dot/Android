import asyncio
import os
import json
from datetime import datetime
from core.event_bus import EventBus
from core.logger import arya_logger
from automation_engine.workflow_builder import WorkflowBuilder

class TriggerDetector:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.workflow_builder = WorkflowBuilder(event_bus)
        
        self.event_bus.subscribe("system.battery.update", self.check_battery_triggers)
        self.event_bus.subscribe("system.location.update", self.check_location_triggers)
        
        self.logger.info("Trigger Detector initialized. I am monitoring your environment for excuses to run workflows, Sir.")
        
        # Start time-based trigger loop
        asyncio.create_task(self._check_time_triggers_loop())

    def _get_all_workflows(self):
        workflows = []
        workflows_dir = self.workflow_builder.workflows_dir
        for filename in os.listdir(workflows_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(workflows_dir, filename), 'r') as f:
                        workflows.append(json.load(f))
                except Exception:
                    pass
        return workflows

    async def _check_time_triggers_loop(self):
        while True:
            now_time = datetime.now().strftime("%H:%M")
            workflows = self._get_all_workflows()
            
            for wf in workflows:
                trigger = wf.get("trigger", {})
                if trigger.get("type") == "time" and trigger.get("value") == now_time:
                    self.logger.info(f"Time trigger matched for workflow: {wf['name']}")
                    await self.event_bus.publish("automation.workflow.execute", {"name": wf['name']})
                    
            # Sleep until the start of the next minute to avoid duplicate triggers
            await asyncio.sleep(60 - datetime.now().second)

    async def check_battery_triggers(self, data: dict):
        level = data.get("level", 100)
        is_charging = data.get("is_charging", False)
        
        workflows = self._get_all_workflows()
        for wf in workflows:
            trigger = wf.get("trigger", {})
            if trigger.get("type") == "battery":
                target_level = trigger.get("level")
                condition = trigger.get("condition", "below") # "below" or "above"
                
                if condition == "below" and level <= target_level and not is_charging:
                    self.logger.info(f"Battery trigger matched for workflow: {wf['name']}")
                    await self.event_bus.publish("automation.workflow.execute", {"name": wf['name']})

    async def check_location_triggers(self, data: dict):
        current_location = data.get("location_name", "").lower()
        
        workflows = self._get_all_workflows()
        for wf in workflows:
            trigger = wf.get("trigger", {})
            if trigger.get("type") == "location":
                target_location = trigger.get("value", "").lower()
                event_type = trigger.get("event", "arrive") # "arrive" or "leave"
                
                # Simplified logic: assuming data contains 'event' (arrive/leave) and 'location_name'
                if current_location == target_location and data.get("event") == event_type:
                    self.logger.info(f"Location trigger matched for workflow: {wf['name']}")
                    await self.event_bus.publish("automation.workflow.execute", {"name": wf['name']})
