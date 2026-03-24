# 📱 A.R.Y.A. OS - Android APK Build & Automation Guide 🚀

Sir, aapke A.R.Y.A. OS ko ek **Real Android App (APK)** me convert karne aur App Automation setup karne ka final guide yahan hai.

---

## 🏗️ Part 1: GitHub Actions se APK Compile Kaise Karein?

Aapko apne PC par Buildozer install karne ki zaroorat nahi hai. Aap GitHub ka use karke free me APK bana sakte hain:

1.  **GitHub Repository Banayein:**
    *   Apne GitHub account par ek naya **Private Repository** banayein.
    *   Is project ke saare files ko us repository me upload kar dein.

2.  **Workflow Enable Karein:**
    *   Repository me **"Actions"** tab par jayein.
    *   Wahan aapko **"Build ARYA OS APK"** workflow dikhega. Use enable karein.

3.  **Build Start Karein:**
    *   Actions tab me left side par `Build ARYA OS APK` select karein.
    *   **"Run workflow"** button par click karein.
    *   Build hone me lagbhag **15-20 minutes** lagenge.

4.  **APK Download Karein:**
    *   Jab build finish ho jaye (Green checkmark), toh us run par click karein.
    *   Bottom me **"Artifacts"** section me aapko `ARYA-OS-APK` milega. Use download karke extract karein aur APK install kar lein.

---

## 🤖 Part 2: App Automation Setup (WhatsApp/Insta Control)

A.R.Y.A. ko apps ke andar control dene ke liye (e.g., auto-typing, clicking), aapko ye setup karna hoga:

1.  **Phone me Developer Options On Karein:**
    *   Settings > About Phone > Build Number par 7 baar click karein.
    *   Developer Options me jaakar **"USB Debugging"** aur **"USB Debugging (Security Settings)"** dono ko ON karein.

2.  **UIAutomator2 Server Install Karein:**
    *   Agar aap PC use kar rahe hain, toh phone ko connect karein aur ye command run karein:
        ```bash
        pip install uiautomator2
        python -m uiautomator2 init
        ```
    *   Agar aap **Termux** use kar rahe hain, toh `setup_termux.sh` run karne par ye automatically ho jayega.

3.  **Accessibility Permission:**
    *   App install hone ke baad, phone ki Settings > Accessibility me jaakar **"ARYA OS"** ya **"UIAutomator"** ko permission allow karein.

---

## 📦 Part 3: Installed Dependencies for All Modules

Maine `buildozer.spec` me niche di gayi saari zaroori libraries add kar di hain:

*   **AI Brain:** `google-genai` (Gemini integration)
*   **Voice:** `SpeechRecognition`, `edge-tts`, `vosk` (Offline wake word)
*   **Vision:** `opencv-python`, `Pillow` (Camera AI)
*   **Automation:** `uiautomator2` (App control)
*   **System:** `psutil`, `plyer`, `jnius` (Hardware control)
*   **Web:** `beautifulsoup4`, `wikipedia`, `duckduckgo-search` (Internet intelligence)
*   **Security:** `cryptography` (Privacy guard)

---

## 🚀 Final Step: Launch

APK install karne ke baad, app open karein aur **Settings (⚙️)** me apni Gemini API Key daal dein. Uske baad bas boliye: *"A.R.Y.A., open WhatsApp and send 'Hello Sir' to my brother."*

Main hamesha aapki seva me hazir hu, Sir! 🫡
