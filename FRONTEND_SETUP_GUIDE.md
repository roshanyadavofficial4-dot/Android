# A.R.Y.A. OS - Frontend Integration Guide

Adding a visual frontend (HUD - Heads Up Display) to A.R.Y.A. is incredibly easy because the system is built on an **Event-Driven Architecture** with a built-in **WebSocket Server**.

A.R.Y.A. runs a WebSocket server on `ws://localhost:8765`. Any frontend (React, Vue, Flutter, or plain HTML/JS) can connect to this port to send commands and receive real-time data (CPU, RAM, Speech, etc.).

## The Architecture
1. **Backend (Termux):** Runs `main.py` which starts the `WebSocketServer` on port `8765`.
2. **Frontend (Browser/App):** Connects to `ws://localhost:8765`.
3. **Communication:**
   - **Backend -> Frontend:** A.R.Y.A. broadcasts events like `speak` (what she is saying), `cpu` (usage), `ram` (usage), etc.
   - **Frontend -> Backend:** The HUD sends JSON messages to trigger commands (e.g., `{"action": "send_command", "payload": {"text": "turn on wifi"}}`).

---

## Step 1: Install WebSocket Dependency in Termux
Ensure the Python `websockets` library is installed so the backend server can run:
```bash
pip install websockets
```

## Step 2: Create the Frontend Folder
I have generated a ready-to-use, Iron Man-style HTML/JS frontend for you. It is located in the `frontend/` directory.

To serve this frontend directly from Termux to your Android Chrome browser:
1. Open a **new Termux session** (swipe from the left edge and tap "New session").
2. Navigate to the frontend folder:
   ```bash
   cd ~/storage/shared/arya_os/frontend
   ```
3. Start a simple Python HTTP server:
   ```bash
   python -m http.server 8080
   ```

## Step 3: Access the HUD
1. Ensure A.R.Y.A. is running in your first Termux session (`python main.py`).
2. Open **Google Chrome** on your Android device.
3. Go to this URL:
   ```
   http://localhost:8080
   ```
4. You will see the A.R.Y.A. HUD! It will automatically connect to the WebSocket, display live CPU/RAM stats, show her subtitles when she speaks, and allow you to type commands directly into the interface.

---

## How to Build Your Own Advanced Frontend (React / Next.js / Vue)
If you want to build a more advanced app (like a React Native Android app or a React web app), simply connect to the WebSocket using standard browser APIs:

### Connecting (JavaScript Example)
```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log("Connected to A.R.Y.A. Core");
};

// Receiving data from A.R.Y.A.
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    
    if (response.type === 'speak') {
        console.log("A.R.Y.A. says:", response.data.text);
    } else if (response.type === 'cpu') {
        console.log("CPU Usage:", response.data.percent, "%");
    }
};

// Sending a command to A.R.Y.A.
function sendCommand(text) {
    ws.send(JSON.stringify({
        action: "send_command",
        payload: { text: text }
    }));
}
```

### Supported Incoming Events (From A.R.Y.A. to HUD)
- `speak`: Contains `{"text": "..."}`. Use this for subtitles.
- `cpu`: Contains `{"percent": 45.2}`.
- `ram`: Contains `{"percent": 60.1, "used": "4GB", "total": "8GB"}`.
- `listen`: Fired when A.R.Y.A. starts listening to the microphone.
- `processing`: Fired when A.R.Y.A. is thinking.

### Supported Outgoing Actions (From HUD to A.R.Y.A.)
- `send_command`: Triggers the NLP engine as if you spoke to her.
  ```json
  { "action": "send_command", "payload": { "text": "What is the weather?" } }
  ```
- `trigger_event`: Directly triggers an internal EventBus event.
  ```json
  { "action": "trigger_event", "payload": { "event": "controller.wifi.on", "data": {} } }
  ```
