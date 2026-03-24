import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from automation_engine.workflow_builder import WorkflowBuilder

class MacroRecorder:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.workflow_builder = WorkflowBuilder(event_bus)
        
        self.is_recording = False
        self.recorded_steps = []
        self.macro_name = ""
        
        self.event_bus.subscribe("automation.macro.start", self.start_recording)
        self.event_bus.subscribe("automation.macro.stop", self.stop_recording)
        self.event_bus.subscribe("ui.click.recorded", self.record_click) # Hooked from Accessibility Driver
        
        self.logger.info("Macro Recorder initialized. I am ready to memorize your repetitive screen tapping, Sir.")

    async def start_recording(self, data: dict):
        self.macro_name = data.get("name", "Untitled Macro")
        self.is_recording = True
        self.recorded_steps = []
        
        self.logger.info(f"Started recording macro: {self.macro_name}")
        await self.event_bus.publish("speak", {"text": f"Recording started for {self.macro_name}. Please perform your actions slowly, Sir. I am a sophisticated AI, not a mind reader."})

    async def record_click(self, data: dict):
        if not self.is_recording:
            return
            
        # Data from Accessibility Driver when user clicks something
        resource_id = data.get("resource_id")
        text = data.get("text")
        description = data.get("description")
        
        step_data = {}
        if resource_id: step_data["resource_id"] = resource_id
        elif text: step_data["text"] = text
        elif description: step_data["description"] = description
        
        if step_data:
            step = {
                "action": "ui.click",
                "data": step_data,
                "abort_on_fail": True
            }
            self.recorded_steps.append(step)
            self.logger.debug(f"Recorded step: {step}")

    async def stop_recording(self, data: dict = None):
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.logger.info(f"Stopped recording macro: {self.macro_name}. Total steps: {len(self.recorded_steps)}")
        
        if self.recorded_steps:
            # Save the recorded steps as a new workflow
            await self.workflow_builder.create_workflow({
                "name": self.macro_name,
                "trigger": {"type": "manual"},
                "steps": self.recorded_steps
            })
            await self.event_bus.publish("speak", {"text": f"Macro recording complete. I have memorized your {len(self.recorded_steps)} steps. Try not to forget what they do."})
        else:
            await self.event_bus.publish("speak", {"text": "You didn't do anything, Sir. I have saved an empty macro, which perfectly reflects the effort put into it."})
