import os
import platform
from pathlib import Path

# ==========================================
# 1. GLOBAL PLATFORM DETECTION
# ==========================================

# Detect the operating system
SYSTEM = platform.system()
# Termux sets the PREFIX environment variable
PREFIX = os.environ.get('PREFIX', '')

# Boolean flags for dynamic adaptation
IS_ANDROID = 'com.termux' in PREFIX or (hasattr(os, 'uname') and 'android' in os.uname().release.lower())
IS_WINDOWS = SYSTEM == 'Windows'
IS_MAC = SYSTEM == 'Darwin'
IS_LINUX = SYSTEM == 'Linux' and not IS_ANDROID

IS_PC = IS_WINDOWS or IS_MAC or IS_LINUX

# ==========================================
# 2. DYNAMIC FILE PATHS
# ==========================================

# Base user directory (Works on Windows, Mac, Linux, and Termux)
HOME_DIR = str(Path.home())

if IS_ANDROID:
    # Hardcoded Android paths
    BASE_STORAGE = '/storage/emulated/0'
    DCIM_DIR = os.path.join(BASE_STORAGE, 'DCIM')
    DOCUMENTS_DIR = os.path.join(BASE_STORAGE, 'Documents')
    MBBS_DIR = os.path.join(DOCUMENTS_DIR, 'MBBS')
    
    # Termux temp directory
    TEMP_AUDIO_FILE = '/tmp/arya_speech.mp3'
else:
    # Standard cross-platform PC paths
    BASE_STORAGE = HOME_DIR
    DCIM_DIR = os.path.join(BASE_STORAGE, 'Pictures')
    DOCUMENTS_DIR = os.path.join(BASE_STORAGE, 'Documents')
    MBBS_DIR = os.path.join(DOCUMENTS_DIR, 'MBBS')
    
    # PC temp directory (OS agnostic)
    import tempfile
    TEMP_AUDIO_FILE = os.path.join(tempfile.gettempdir(), 'arya_speech.mp3')

def get_dynamic_path(android_path: str, pc_path: str) -> str:
    """Helper to fetch the correct path based on the environment."""
    return android_path if IS_ANDROID else pc_path
