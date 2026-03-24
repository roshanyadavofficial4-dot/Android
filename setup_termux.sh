#!/bin/bash

echo "===================================================="
echo "   A.R.Y.A. OS - Termux Environment Setup Script      "
echo "===================================================="

echo "[*] Requesting Android Storage Access..."
termux-setup-storage
sleep 2

echo "[*] Updating and upgrading package repositories..."
pkg update -y && pkg upgrade -y

echo "[*] Installing core system dependencies..."
# Python, C/C++ compilers, and math/crypto libraries needed for heavy AI/Vision modules
pkg install python clang libxml2 libxslt openblas libffi openssl termux-api -y

echo "[*] Upgrading pip to the latest version..."
pip install --upgrade pip

echo "[*] Installing Python requirements for A.R.Y.A. OS..."
# This will install google-genai, opencv-python-headless, psutil, pyjnius, etc.
pip install -r requirements.txt

echo "===================================================="
echo "   Setup Complete. A.R.Y.A. OS is ready for Alpha.    "
echo "===================================================="
echo ""
echo "CRITICAL REMINDER: "
echo "1. Ensure you have exported your GEMINI_API_KEY."
echo "2. Go to Android Settings > Accessibility and enable the service for Termux."
echo ""
echo "To initiate the boot sequence, run: python main.py"
