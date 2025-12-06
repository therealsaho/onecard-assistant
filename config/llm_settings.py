"""
LLM Configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Mode: 'gemini' for Real, anything else for Mock
USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "gemini"

# API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Model Name
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
