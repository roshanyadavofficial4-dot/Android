import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger
from google.genai import GoogleGenAI

class AutonomousAgent:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_executing = False
        
        self.event_bus.subscribe("automation.agent.execute", self.execute_complex_task)
        self.logger.info("Project Autonomous Agent (Do-It-For-Me Mode) initialized. I'll handle the details, Sir.")

    async def execute_complex_task(self, data: dict):
        if self.is_executing:
            return
        
        self.is_executing = True
        task_description = data.get("task")
        self.logger.info(f"Autonomous Agent: Executing complex task: {task_description}")
        await self.event_bus.publish("speak", {"text": f"Understood, Sir. I'm initiating the autonomous sequence for: {task_description}. Please stand by."})

        try:
            # 1. Plan the task using Gemini
            plan_prompt = f"""
            You are the A.R.Y.A. OS Autonomous Agent. 
            The user wants you to perform a complex task: "{task_description}". 
            
            You have access to the following tools:
            - search_web(query)
            - open_app(app_name)
            - read_screen()
            - click_element(text_or_id)
            - type_text(text)
            - wait(seconds)
            
            Please provide a STEP-BY-STEP plan to execute this task. 
            Format: JSON list of actions.
            Example: [
                {{"action": "search_web", "query": "flights to Delhi under 5k"}},
                {{"action": "open_app", "app_name": "chrome"}},
                {{"action": "read_screen"}},
                {{"action": "click_element", "text": "Book Now"}}
            ]
            """
            
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.logger.error("GEMINI_API_KEY not found. Cannot execute autonomous task.")
                self.is_executing = False
                return

            ai = GoogleGenAI(apiKey=api_key)
            response = await ai.models.generateContent({
                "model": "gemini-3.1-flash-preview",
                "contents": plan_prompt
            })
            
            # Parse the plan (Simulated: in a real app, we'd use responseSchema)
            plan_text = response.text.strip()
            # Extract JSON from markdown if needed
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0].strip()

            import json
            try:
                plan = json.loads(plan_text)
            except:
                self.logger.error(f"Failed to parse plan: {plan_text}")
                await self.event_bus.publish("speak", {"text": "I'm having trouble formulating a stable plan for this task, Sir."})
                self.is_executing = False
                return

            # 2. Execute the plan step-by-step
            for step in plan:
                action = step.get("action")
                params = step
                self.logger.info(f"Executing step: {action} with params: {params}")
                
                # Map actions to internal events
                if action == "search_web":
                    await self.event_bus.publish("web.search", {"query": params.get("query")})
                elif action == "open_app":
                    await self.event_bus.publish("app.launch", {"app_name": params.get("app_name")})
                elif action == "read_screen":
                    await self.event_bus.publish("vision.screen.read", {})
                elif action == "click_element":
                    await self.event_bus.publish("app.auto_click", {"text": params.get("text")})
                elif action == "type_text":
                    await self.event_bus.publish("app.auto_type", {"text": params.get("text")})
                elif action == "wait":
                    await asyncio.sleep(params.get("seconds", 2))
                
                # Wait for each step to stabilize
                await asyncio.sleep(3)

            await self.event_bus.publish("speak", {"text": f"The task '{task_description}' has been executed to the best of my ability, Sir. Awaiting your final confirmation."})

        except Exception as e:
            self.logger.error(f"Autonomous agent execution failed: {e}")
            await self.event_bus.publish("speak", {"text": "My autonomous sequence has encountered a critical error, Sir. I've halted the operation for safety."})
        finally:
            self.is_executing = False
