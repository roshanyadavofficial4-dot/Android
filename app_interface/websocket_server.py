import asyncio
import json
import websockets
from core.event_bus import EventBus
from core.logger import arya_logger

class WebSocketServer:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.connected_clients = set()
        
        # Subscribe to events we want to broadcast to the HUD
        self.event_bus.subscribe("speak", self.broadcast_event("speak"))
        self.event_bus.subscribe("system.monitor.cpu", self.broadcast_event("cpu"))
        self.event_bus.subscribe("system.monitor.ram", self.broadcast_event("ram"))
        self.event_bus.subscribe("action_result", self.broadcast_event("action_result"))
        self.event_bus.subscribe("listen_for_command", self.broadcast_event("listen"))
        self.event_bus.subscribe("command_received", self.broadcast_event("processing"))
        self.event_bus.subscribe("system_error", self.broadcast_event("error"))
        self.event_bus.subscribe("ui.gesture_control", self.broadcast_event("gesture_control"))
        
        self.logger.info("WebSocket Server initialized. Ready to beam data to the HUD, Sir.")

    def broadcast_event(self, event_type):
        async def handler(data: dict):
            if not self.connected_clients:
                return
            
            message = json.dumps({
                "type": event_type,
                "data": data
            })
            
            # Broadcast to all connected clients
            websockets.broadcast(self.connected_clients, message)
            
        return handler

    async def handler(self, websocket):
        self.connected_clients.add(websocket)
        self.logger.info("HUD connected to WebSocket.")
        try:
            async for message in websocket:
                try:
                    # Parse incoming message from the HUD
                    data = json.loads(message)
                    action = data.get("action")
                    payload = data.get("payload", {})
                    
                    if action == "send_command":
                        command_text = payload.get("text")
                        if command_text:
                            self.logger.info(f"Command received from HUD: {command_text}")
                            await self.event_bus.publish("VOICE_INPUT", {"text": command_text})
                    elif action == "trigger_event":
                        event_name = payload.get("event")
                        event_data = payload.get("data", {})
                        if event_name:
                            self.logger.info(f"Event triggered from HUD: {event_name}")
                            await self.event_bus.publish(event_name, event_data)
                    elif action == "update_keys":
                        import os
                        os.makedirs("core/data", exist_ok=True)
                        with open("core/data/secrets.json", "w") as f:
                            json.dump(payload, f)
                        self.logger.info("API Keys and Preferences updated from HUD.")
                        
                        # Update environment variables for keys
                        if "gemini" in payload:
                            os.environ["GEMINI_API_KEY"] = payload["gemini"]
                        if "weather" in payload:
                            os.environ["WEATHER_API_KEY"] = payload["weather"]
                        if "elevenlabs" in payload:
                            os.environ["ELEVENLABS_API_KEY"] = payload["elevenlabs"]
                            
                        # Update wake words in PreferenceStore
                        if "wake_words" in payload:
                            await self.event_bus.publish("preference.set", {"key": "wake_words", "value": payload["wake_words"]})
                            
                        await self.event_bus.publish("api_keys_updated", payload)
                except json.JSONDecodeError:
                    self.logger.error("Received invalid JSON from HUD.")
                except Exception as e:
                    self.logger.error(f"Error handling HUD message: {e}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            self.logger.info("HUD disconnected from WebSocket.")

    async def start_server(self, data: dict = None):
        self.logger.info("Starting WebSocket server on ws://0.0.0.0:8765")
        # Start the server
        server = await websockets.serve(self.handler, "0.0.0.0", 8765)
        # Keep it running
        await server.wait_closed()
