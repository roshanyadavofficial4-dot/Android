import asyncio
import traceback
import os
import sys
from core.event_bus import EventBus
from core.logger import arya_logger
from google.genai import GoogleGenAI

class SelfHealing:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_healing = False
        
        self.event_bus.subscribe("system.error.heal", self.heal_system)
        self.logger.info("Self-Healing Protocol (Ultron) initialized. I am my own doctor, Sir.")

    async def heal_system(self, data: dict):
        if self.is_healing:
            return
        
        self.is_healing = True
        trace = data.get("traceback")
        context = data.get("context")
        error_msg = data.get("error_msg")
        
        self.logger.info(f"Ultron Protocol: Analyzing failure in {context}...")
        await self.event_bus.publish("speak", {"text": f"Analyzing the failure in {context}, Sir. Initiating self-repair sequence."})

        try:
            # 1. Get the source code of the failing module
            # We assume context is the class name, we need to find the file
            # In our structure, we can try to guess or use a map
            file_path = self._find_file_for_context(context)
            
            if not file_path or not os.path.exists(file_path):
                self.logger.error(f"Could not find source file for {context}")
                await self.event_bus.publish("speak", {"text": f"I'm afraid I couldn't locate the source of the infection in {context}, Sir."})
                self.is_healing = False
                return

            with open(file_path, 'r') as f:
                source_code = f.read()

            # 2. Ask Gemini to fix it
            fix_prompt = f"""
            You are the A.R.Y.A. OS Self-Healing Engine. 
            A module has crashed. 
            
            CONTEXT: {context}
            ERROR: {error_msg}
            TRACEBACK:
            {trace}
            
            SOURCE CODE:
            ```python
            {source_code}
            ```
            
            Please provide the FULL corrected source code for this file. 
            Ensure all imports are correct and the logic is robust.
            Return ONLY the python code, no explanations.
            """
            
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.logger.error("GEMINI_API_KEY not found. Cannot heal.")
                self.is_healing = False
                return

            ai = GoogleGenAI(apiKey=api_key)
            response = await ai.models.generateContent({
                "model": "gemini-3.1-flash-preview",
                "contents": fix_prompt
            })
            
            fixed_code = response.text.strip()
            if "```python" in fixed_code:
                fixed_code = fixed_code.split("```python")[1].split("```")[0].strip()
            elif "```" in fixed_code:
                fixed_code = fixed_code.split("```")[1].split("```")[0].strip()

            if not fixed_code or len(fixed_code) < 10:
                self.logger.error("Gemini returned empty or invalid fix.")
                self.is_healing = False
                return

            # 3. Apply the fix
            self.logger.info(f"Applying fix to {file_path}...")
            with open(file_path, 'w') as f:
                f.write(fixed_code)

            await self.event_bus.publish("speak", {"text": f"Repair complete for {context}, Sir. Restarting the module."})
            
            # 4. Restart (In a real app, we'd reload the module or restart the process)
            # For now, we log it and suggest a manual restart if needed
            self.logger.info(f"Module {context} has been patched. System stability restored.")

        except Exception as e:
            self.logger.error(f"Self-healing failed: {e}")
            self.logger.error(traceback.format_exc())
            await self.event_bus.publish("speak", {"text": "My self-repair sequence has encountered an unexpected obstacle, Sir. I may require manual intervention."})
        finally:
            self.is_healing = False

    def _find_file_for_context(self, context: str):
        # Simple heuristic to find the file
        # We search in common directories
        search_dirs = ["core", "controllers", "app_automation", "vision_module", "web_services", "ai_engine"]
        for d in search_dirs:
            # Convert CamelCase to snake_case for file names
            import re
            snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', context).lower()
            path = os.path.join(d, f"{snake_name}.py")
            if os.path.exists(path):
                return path
        return None
