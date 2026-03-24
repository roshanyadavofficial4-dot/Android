# A.R.Y.A. OS - Termux Setup Guide

Welcome to the A.R.Y.A. OS installation guide for Android (via Termux). This guide will walk you through setting up the environment, installing dependencies, and running your personal AI assistant.

## Prerequisites
1. Install **Termux** from F-Droid (Do NOT use the Google Play Store version, it is outdated).
2. Install **Termux:API** from F-Droid.

## Step 1: System Update & Core Packages
Open Termux and run the following commands to update the system and install core dependencies:

```bash
pkg update && pkg upgrade -y
pkg install python git clang make libffi openssl libjpeg-turbo -y
pkg install termux-api -y
```

## Step 2: Clone the Repository
Clone the A.R.Y.A. OS repository to your local storage:

```bash
termux-setup-storage
# Grant storage permission when prompted
cd ~/storage/shared
git clone <YOUR_REPO_URL> arya_os
cd arya_os
```

## Step 3: Install Python Dependencies
A.R.Y.A. requires several Python libraries to function.

```bash
pip install --upgrade pip
pip install google-genai edge-tts SpeechRecognition gTTS psutil websockets aiohttp
```

### Advanced Dependencies (Optional but Recommended)
For Vision and advanced automation, you may need additional libraries. Note that some of these can be tricky to compile on Android.

```bash
# For Vision Module (Camera, Face Recognition, OCR)
pkg install opencv-python -y
pip install pytesseract pyzbar mediapipe

# For hardware control via Python
pip install plyer jnius
```

## Step 4: Voice Control & Permissions
To control A.R.Y.A. by voice, you must grant Termux permission to use the microphone.

1.  Go to **Android Settings** -> **Apps** -> **Termux** -> **Permissions**.
2.  Enable **Microphone** and **Storage**.
3.  Ensure **Termux:API** is also granted these permissions.
4.  **IMPORTANT (Background Listening):** To ensure A.R.Y.A. listens when the screen is off, you must disable battery optimization for Termux. Go to **Settings** -> **Battery** -> **Battery Optimization** -> **All Apps** -> **Termux** -> **Don't Optimize**.
5.  **Root Access (Optional but Recommended):** To allow A.R.Y.A. to automatically toggle **Mobile Data**, your device must be **Rooted**. She uses the `su -c svc data enable` command. If not rooted, she will simply inform you that she lacks the authority.

### How to use Voice Commands:
*   **Method 1 (HUD):** Open the Frontend HUD (see Step 6) and click the **Microphone Icon**. When it pulses red, speak your command.
*   **Method 2 (Background):** A.R.Y.A. has a background wake-word listener. Say "A.R.Y.A." or "Jarvis" to activate her (requires `SpeechRecognition` and a quiet environment). This works even when the screen is off!

## Step 5: Offline Mode & Intelligence
A.R.Y.A. is now equipped with an **Offline Brain**.
*   **Offline:** She can control system settings (WiFi, Bluetooth, Flashlight, etc.) without an internet connection.
*   **Auto-Data:** If you ask for something that requires the internet (like a web search) while offline, she will automatically attempt to turn on your mobile data, perform the task, and then respond.
*   **Intelligence:** She uses her local reasoning engine to decide when she needs to go online.

## Step 6: API Key Configuration
A.R.Y.A. uses the Gemini API for its core intelligence. The key has been injected into the codebase, but you can also set it as an environment variable for safety.

```bash
export GEMINI_API_KEY="AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was"
```
*(Tip: Add this line to your `~/.bashrc` to make it permanent).*

## Step 6: Frontend HUD Setup (The JARVIS Interface)
To see the HUD and control A.R.Y.A. visually:

1.  In a new Termux session, navigate to the `frontend` directory:
    ```bash
    cd ~/storage/shared/arya_os/frontend
    ```
2.  Start a simple HTTP server:
    ```bash
    python -m http.server 8080
    ```
3.  Open your mobile browser (Chrome/Firefox) and go to: `http://localhost:8080`
4.  The HUD will automatically connect to A.R.Y.A.'s WebSocket server (port 8765).

## Step 7: Booting A.R.Y.A.
Once everything is installed, you can boot the OS:

```bash
python main.py
```

---

## 📱 Android App Control
You can turn the HUD into a standalone "app" on your Android home screen:
1.  Open `http://localhost:8080` in Chrome on your phone.
2.  Tap the **three dots (menu)** in the top right.
3.  Select **"Add to Home screen"**.
4.  Now you have a JARVIS-style app icon to launch the HUD instantly!

## Step 8: App Automation Setup (UIAutomator2)
To allow A.R.Y.A. to control other apps (WhatsApp, Instagram, etc.) directly from Termux, follow these steps:

1.  **Install Android Tools & UIAutomator2:**
    ```bash
    pkg install android-tools -y
    pip install uiautomator2
    ```

2.  **Enable Wireless ADB (Crucial for same-device control):**
    *   Go to **Settings** -> **Developer Options**.
    *   Enable **Wireless Debugging**.
    *   Tap on "Wireless Debugging" to see the **IP address and Port** (e.g., `192.168.1.5:45678`).

3.  **Connect Termux to your Phone:**
    *   In Termux, run:
        ```bash
        adb connect localhost:<PORT_FROM_STEP_2>
        ```
    *   Accept the "Allow USB Debugging?" prompt on your screen.

4.  **Initialize the Automation Agent:**
    *   Run this command to install the necessary "ATX" agent on your phone:
        ```bash
        python -m uiautomator2 init
        ```
    *   A small app called "ATX" will be installed. Open it and ensure it has "Display over other apps" permission.

5.  **Test Automation:**
    *   Now A.R.Y.A. can use the `app_automation` module to click buttons, type messages, and scroll through apps according to your voice commands.

---

## 🛠️ Troubleshooting & Error Handling

### Error: `websockets: command not found` or `No module named websockets`
**Cause:** The `websockets` package is missing.
**Fix:** Run `pip install websockets`.

### Error: `System logs overlapping reactor animation`
**Fix:** I have updated the HUD layout. The **Arc Reactor** is now in the `left-panel` and the **System Logs** are in the `right-panel`. In landscape mode, they appear side-by-side. In portrait mode, they are stacked. They will no longer overlap.

### Error: `Voice is robotic`
**Cause:** Using `gTTS` or `pyttsx3` instead of `edge-tts`.
**Fix:** A.R.Y.A. is now configured to use **Microsoft Edge TTS** for human-like voices. Ensure you have an active internet connection for the best quality. Hindi and English are both supported automatically.
