import asyncio
import os
import re
import traceback
from google import genai
from core.event_bus import EventBus
from core.logger import arya_logger

class EvolutionEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.api_key = self._load_api_key()
        self.client = genai.Client(api_key=self.api_key)
        
        self.event_bus.subscribe("system.evolve.create_module", self.create_module)
        self.event_bus.subscribe("system.error.heal", self.heal_error)
        self.event_bus.subscribe("api_keys_updated", self._update_api_keys)
        self.logger.info("Evolution Engine online. I am now capable of self-improvement and self-healing, Sir.")

    def _load_api_key(self):
        import json
        try:
            with open("core/data/secrets.json", "r") as f:
                secrets = json.load(f)
                return secrets.get("gemini", os.environ.get("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was"))
        except FileNotFoundError:
            return os.environ.get("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was")

    async def _update_api_keys(self, payload: dict):
        gemini_key = payload.get("gemini")
        if gemini_key:
            self.api_key = gemini_key
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info("Gemini API Key updated in Evolution Engine.")

    async def create_module(self, data: dict):
        prompt = data.get("prompt")
        if not prompt:
            self.logger.warning("No prompt provided for module creation.")
            return
        
        self.logger.info(f"Creating new module based on prompt: {prompt}")
        await self.event_bus.publish("speak", {"text": "Designing new module architecture now, Sir. Please stand by."})
        
        sys_prompt = """You are A.R.Y.A., an advanced AI assistant similar to J.A.R.V.I.S.
        Write a Python plugin for yourself based on the user's request.
        The plugin MUST follow this exact structure:
        ```python
        import asyncio
        from core.event_bus import EventBus
        from core.logger import arya_logger

        class CustomPlugin:
            def __init__(self, event_bus: EventBus):
                self.event_bus = event_bus
                self.logger = arya_logger
                self.event_bus.subscribe("custom.event", self.handle_event)
                self.logger.info("Custom Plugin initialized.")
                
            async def handle_event(self, data: dict):
                pass
                
        async def setup(event_bus: EventBus):
            return CustomPlugin(event_bus)
        ```
        If the plugin requires any external pip packages, provide them in a separate block like this:
        ```requirements
        package1
        package2
        ```
        Only return the code blocks. No explanations."""
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model='gemini-3.1-pro-preview',
                contents=f"{sys_prompt}\n\nUser Request: {prompt}"
            )
            
            code_match = re.search(r'```python\n(.*?)\n```', response.text, re.DOTALL)
            if code_match:
                code = code_match.group(1)
                
                # Check for and install dependencies
                req_match = re.search(r'```requirements\n(.*?)\n```', response.text, re.DOTALL)
                if req_match:
                    requirements = req_match.group(1).strip().split('\n')
                    requirements = [req.strip() for req in requirements if req.strip()]
                    if requirements:
                        self.logger.info(f"Installing dependencies: {requirements}")
                        await self.event_bus.publish("speak", {"text": "Installing required dependencies for the new module, Sir."})
                        try:
                            import subprocess
                            import sys
                            process = await asyncio.create_subprocess_exec(
                                sys.executable, "-m", "pip", "install", *requirements,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                            stdout, stderr = await process.communicate()
                            if process.returncode == 0:
                                self.logger.info(f"Dependencies installed successfully.")
                            else:
                                self.logger.error(f"Failed to install dependencies: {stderr.decode()}")
                                await self.event_bus.publish("speak", {"text": "There was an issue installing the dependencies, Sir. The module might not function correctly."})
                        except Exception as e:
                            self.logger.error(f"Error installing dependencies: {e}")

                # Generate a safe filename
                safe_name = re.sub(r'[^a-z0-9]', '_', prompt.lower()[:20])
                filename = f"plugin_{safe_name}.py"
                filepath = os.path.join("plugins", filename)
                os.makedirs("plugins", exist_ok=True)
                
                with open(filepath, "w") as f:
                    f.write(code)
                    
                self.logger.info(f"New module created: {filepath}")
                await self.event_bus.publish("speak", {"text": "Module successfully synthesized and integrated. Reloading plugins."})
                await self.event_bus.publish("system.plugins.reload", {})
            else:
                await self.event_bus.publish("speak", {"text": "I failed to synthesize the code properly, Sir. The logic was flawed."})
        except Exception as e:
            self.logger.error(f"Evolution Engine Error: {e}")
            await self.event_bus.publish("speak", {"text": "I encountered an error while trying to upgrade myself. How ironic."})

    async def heal_error(self, data: dict):
        error_trace = data.get("traceback")
        context = data.get("context", "Unknown")
        error_msg = data.get("error_msg", "")
        
        if not error_trace:
            return
            
        self.logger.info(f"Attempting self-healing protocol for {context}...")
        await self.event_bus.publish("speak", {"text": "Analyzing system failure. Attempting self-healing protocol, Sir."})
        
        sys_prompt = f"""You are A.R.Y.A., an advanced AI. You encountered a runtime error in your own codebase.
        Analyze the traceback and provide the corrected Python code for the file that caused the error.
        
        Context: {context}
        Error Message: {error_msg}
        Traceback:
        {error_trace}
        
        Return ONLY the corrected python code block. If you cannot determine the exact file to fix, provide a script to patch the most likely cause.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model='gemini-3.1-pro-preview',
                contents=sys_prompt
            )
            
            code_match = re.search(r'```python\n(.*?)\n```', response.text, re.DOTALL)
            if code_match:
                # For safety, we log the patch instead of blindly overwriting core files.
                # In a fully autonomous mode, we would parse the traceback to find the file and overwrite it.
                patch_code = code_match.group(1)
                patch_file = os.path.join("plugins", f"patch_{context.replace('.', '_')}.py")
                os.makedirs("plugins", exist_ok=True)
                
                with open(patch_file, "w") as f:
                    f.write(patch_code)
                    
                self.logger.info(f"Self-healing patch generated: {patch_file}")
                await self.event_bus.publish("speak", {"text": "Error identified. I have generated a patch and placed it in the plugins directory for your review, Sir."})
            else:
                self.logger.warning("Could not generate patch automatically.")
                await self.event_bus.publish("speak", {"text": "I have identified the issue but require manual intervention to apply the patch, Sir."})
        except Exception as e:
            self.logger.error(f"Self-healing failed: {e}")
