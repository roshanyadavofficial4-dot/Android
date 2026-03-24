import json
import os
import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class WorkflowBuilder:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.workflows_dir = "memory_system/workflows"
        
        os.makedirs(self.workflows_dir, exist_ok=True)
        
        self.event_bus.subscribe("automation.workflow.create", self.create_workflow)
        self.event_bus.subscribe("automation.workflow.list", self.list_workflows)
        
        self.logger.info("Workflow Builder initialized. Ready to automate your mundane existence, Sir.")
        self._create_default_workflows()

    def _create_default_workflows(self):
        # Create a default 'Study Mode' if it doesn't exist
        study_mode_path = os.path.join(self.workflows_dir, "study_mode.json")
        if not os.path.exists(study_mode_path):
            study_mode = {
                "name": "Study Mode",
                "description": "Turns off distractions and opens study materials.",
                "trigger": {"type": "manual"},
                "steps": [
                    {"action": "system.wifi.set", "data": {"state": "off"}, "abort_on_fail": False},
                    {"action": "system.volume.set", "data": {"level": 30}, "abort_on_fail": False},
                    {"action": "app.launch", "data": {"app_name": "adobe reader"}, "abort_on_fail": True},
                    {"action": "media.music.play", "data": {"genre": "lo-fi"}, "abort_on_fail": False}
                ]
            }
            with open(study_mode_path, 'w') as f:
                json.dump(study_mode, f, indent=4)

    async def create_workflow(self, data: dict):
        name = data.get("name")
        steps = data.get("steps", [])
        trigger = data.get("trigger", {"type": "manual"})
        
        if not name or not steps:
            self.logger.error("Cannot create a workflow without a name and steps.")
            return

        filename = name.lower().replace(" ", "_") + ".json"
        filepath = os.path.join(self.workflows_dir, filename)
        
        workflow_data = {
            "name": name,
            "trigger": trigger,
            "steps": steps
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(workflow_data, f, indent=4)
            self.logger.info(f"Workflow '{name}' saved successfully.")
            await self.event_bus.publish("speak", {"text": f"Workflow '{name}' has been created. I shall add it to my ever-growing list of chores."})
        except Exception as e:
            self.logger.error(f"Failed to save workflow '{name}': {e}")

    def get_workflow(self, name: str) -> dict:
        filename = name.lower().replace(" ", "_") + ".json"
        filepath = os.path.join(self.workflows_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading workflow {name}: {e}")
        return None

    async def list_workflows(self, data: dict = None):
        workflows = []
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith(".json"):
                workflows.append(filename.replace(".json", "").replace("_", " ").title())
                
        if workflows:
            wf_list = ", ".join(workflows)
            await self.event_bus.publish("speak", {"text": f"Your current automated routines are: {wf_list}."})
        else:
            await self.event_bus.publish("speak", {"text": "You have no workflows configured. You are living life on manual mode, Sir."})
