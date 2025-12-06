"""
Audio configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# STT Provider: 'mock' or 'whisper'
# STT Provider: 'mock', 'whisper', 'faster-whisper', or 'google'
STT_PROVIDER = os.getenv("STT_PROVIDER", "mock").lower()

# Faster Whisper Model: 'tiny', 'base', 'small', 'medium', 'large-v2'
FASTER_WHISPER_MODEL = os.getenv("FASTER_WHISPER_MODEL", "tiny")

# TTS Provider: 'mock' or 'gtts'
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "mock").lower()

# Max upload size in MB
UPLOAD_MAX_SIZE_MB = int(os.getenv("UPLOAD_MAX_SIZE_MB", "5"))

# Temporary directory for audio files
# Use a local tmp directory to avoid permission issues on some systems, or use system tmp
AUDIO_TMP_DIR = os.getenv("AUDIO_TMP_DIR", os.path.join(os.getcwd(), "tmp_audio"))

# Ensure tmp dir exists
os.makedirs(AUDIO_TMP_DIR, exist_ok=True)
