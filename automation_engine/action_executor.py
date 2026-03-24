import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from automation_engine.workflow_builder import WorkflowBuilder

class ActionExecutor:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.workflow_builder = WorkflowBuilder(event_bus)
        
        self.event_bus.subscribe("automation.workflow.execute", self.execute_workflow)
        self.logger.info("Action Executor initialized. I am ready to blindly follow your JSON instructions, Sir.")

    async def execute_workflow(self, data: dict):
        workflow_name = data.get("name")
        if not workflow_name:
            return

        workflow = self.workflow_builder.get_workflow(workflow_name)
        if not workflow:
            self.logger.error(f"Workflow '{workflow_name}' not found.")
            await self.event_bus.publish("speak", {"text": f"I cannot execute '{workflow_name}' because it does not exist. Did you imagine it, Sir?"})
            return

        steps = workflow.get("steps", [])
        self.logger.info(f"Executing workflow: {workflow['name']} ({len(steps)} steps)")
        await self.event_bus.publish("speak", {"text": f"Initiating {workflow['name']} protocol."})

        for i, step in enumerate(steps):
            action = step.get("action")
            payload = step.get("data", {})
            abort_on_fail = step.get("abort_on_fail", True)
            
            self.logger.info(f"Step {i+1}/{len(steps)}: Executing '{action}' with {payload}")
            
            try:
                # Publish the action to the event bus
                await self.event_bus.publish(action, payload)
                
                # Wait a moment for the action to complete (UI transitions take time)
                # In a highly advanced system, we'd wait for a specific 'action_result' event here.
                await asyncio.sleep(2.0) 
                
            except Exception as e:
                self.logger.error(f"Error executing step {i+1} ({action}): {e}")
                if abort_on_fail:
                    self.logger.warning(f"Aborting workflow '{workflow['name']}' due to failure in step {i+1}.")
                    await self.event_bus.publish("speak", {"text": f"Workflow aborted. Step {i+1} failed spectacularly. You might want to look into that."})
                    return
                else:
                    self.logger.info(f"Continuing workflow despite failure in step {i+1}.")

        self.logger.info(f"Workflow '{workflow['name']}' completed successfully.")
        await self.event_bus.publish("speak", {"text": f"{workflow['name']} protocol complete. At your service."})
