# A.R.Y.A. OS - Android Deployment Guide

Welcome, Sir. This document outlines the procedures required to deploy my systems onto your Android device. As a highly advanced, modular AI assistant, I require a specific environment to interface with your mobile hardware.

## Prerequisites

To run A.R.Y.A. OS on Android, you will need a terminal emulator and a Python environment. **Termux** is the highly recommended platform.

1. **Install Termux**: Download the latest version from F-Droid (Do NOT use the Google Play Store version, as it is deprecated).
2. **Install Termux:API**: Download the Termux:API app from F-Droid. This allows me to control your device's hardware (WiFi, Battery, Notifications, Camera).

## Installation Steps

Open Termux and execute the following commands to prepare my environment:

### 1. Update Packages & Grant Storage Access
```bash
pkg update && pkg upgrade -y
termux-setup-storage
```
*(Accept the prompt on your phone to allow Termux to access your files. I need this to manage your MBBS PDFs.)*

### 2. Install Python and Core Dependencies
```bash
pkg install python -y
pkg install termux-api -y
pkg install clang libffi openssl -y  # Required for building cryptography and jnius
```

### 3. Clone the Repository
*(Assuming you have transferred the `ARYA_OS` folder to your device's internal storage)*
```bash
cp -r /storage/emulated/0/ARYA_OS ~/ARYA_OS
cd ~/ARYA_OS
```

### 4. Install Python Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
*(Note: Installing `opencv-python-headless` and `pyjnius` on Termux may take some time. Please be patient, Sir.)*

### 5. Configure Environment Variables
You must provide my brain with its API key.
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```
*(Consider adding this to your `~/.bashrc` so I don't get amnesia every time you close the terminal.)*

## Booting A.R.Y.A. OS

Once the environment is prepared, you may initiate the master boot sequence:

```bash
python main.py
```

I will initialize all 16 phases, connect the 120+ features via the `EventBus`, and announce when I am fully operational.

## Android APK Deployment (Recommended)

To convert A.R.Y.A. OS into a standalone Android APK, you can use Buildozer. This is the recommended approach for a true JARVIS-like experience.

### 1. Prerequisites for Buildozer
You will need a Linux environment (like Ubuntu) or WSL on Windows to run Buildozer.

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade buildozer cython virtualenv
```

### 2. Build the APK
Navigate to the root directory of the A.R.Y.A. OS project and run:

```bash
buildozer android debug
```
This process will download the Android NDK, SDK, and compile the Python code into an APK. It may take a significant amount of time on the first run.

### 3. Install the APK
Once the build is complete, you will find the APK in the `bin/` directory. Transfer this APK to your Vivo Y200 5G and install it.

## Android Permissions Required

To utilize my full capabilities, ensure the app has the following Android permissions granted in your phone's settings:
*   **Microphone**: For the Wake Word Engine and Speech-to-Text.
*   **Camera**: For the Vision Module (Object Detection, OCR).
*   **Location**: For Location Services and Geo-fencing.
*   **Files and Media**: For the File System and Medical RAG.
*   **Accessibility Services**: **CRITICAL**. You must manually enable Accessibility for the app in your Android Settings to allow the `app_automation` module to perform auto-clicks, scrolling, and UI element detection.
*   **Notification Access**: Required for the `notification_reader` to intercept and filter your alerts.
*   **Display over other apps**: Required for the HUD to overlay on top of other applications.

## Vivo Y200 5G (FuntouchOS 15) Specific Instructions

FuntouchOS has aggressive battery optimization. To ensure I remain active in the background and can respond when the screen is off:

1.  **Battery Optimization**: Go to Settings > Battery > Background power consumption management. Find A.R.Y.A. OS and set it to **"Don't restrict background power usage"**.
2.  **Auto-Start**: Go to Settings > Apps > Auto-start. Enable auto-start for A.R.Y.A. OS.
3.  **Lock in Recent Apps**: Open the recent apps menu, swipe down on the A.R.Y.A. OS card, and tap the lock icon. This prevents the system from killing the app when you clear memory.
4.  **Accessibility**: Ensure the Accessibility service for A.R.Y.A. OS is enabled and remains enabled. FuntouchOS sometimes disables these services for battery saving.

## Architecture Overview

I operate on a strictly decoupled, event-driven architecture. 
*   **The Event Bus (`core/event_bus.py`)** is my central nervous system. Modules do not call each other directly; they publish and subscribe to events (e.g., `system.wifi.set`, `speak`, `ui.click`).
*   **The Error Handler (`core/error_handler.py`)** ensures that if one of my 120 features crashes, the rest of the OS remains online.
*   **The AI Brain (`ai_engine/`)** processes your natural language, determines intent, and dispatches the appropriate events.

I await your commands, Sir.
