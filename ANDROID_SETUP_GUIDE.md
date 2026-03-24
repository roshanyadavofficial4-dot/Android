# 📱 A.R.Y.A. OS - Android Setup Guide

To ensure A.R.Y.A. OS runs smoothly and has full control over your device, follow these steps:

## 1. Developer Options
*   Go to **Settings > About Phone**.
*   Tap **Build Number** 7 times to enable Developer Options.
*   Go to **Settings > System > Developer Options**.
*   Enable **USB Debugging** (Required for `uiautomator2` automation).
*   Enable **Wireless Debugging** (Optional, but useful).

## 2. Battery Optimization (Crucial)
*   Go to **Settings > Apps > A.R.Y.A. OS**.
*   Select **Battery**.
*   Choose **Unrestricted** (This prevents Android from killing the background wake word listener).

## 3. Accessibility Services
*   Go to **Settings > Accessibility**.
*   Find **A.R.Y.A. OS** (or the Python/Kivy app name).
*   Turn it **ON** (Required for Screen Reading, Auto-Clicking, and App Automation).

## 4. Permissions
Ensure the following permissions are granted manually if not prompted:
*   **Microphone:** For Voice Commands and Wake Word.
*   **Camera:** For Gaze Tracking and Vision AI.
*   **Storage:** For File Management.
*   **Notifications:** For system alerts.
*   **Draw over other apps:** Required for the JARVIS HUD to appear on top of other apps.

## 5. Termux Setup (If running via Termux)
If you are using Termux instead of the APK:
*   Run `termux-setup-storage`.
*   Install Python: `pkg install python`.
*   Install dependencies: `pip install -r requirements.txt`.
*   Run the OS: `python main.py`.

---
**"System optimization is complete, Sir. Once these settings are applied, I will have full tactical control."** 🕶️
