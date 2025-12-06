import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini_client import GeminiLLMClient
from config.llm_settings import GEMINI_MODEL_NAME

print(f"Testing Gemini Client with model: {GEMINI_MODEL_NAME}")

# Force real mode for this test, assuming env vars are set or we want to test the default
# Note: config.llm_settings reads env vars at import. 
# If USE_REAL_LLM is not set in env, it defaults to mock.
# We want to verify the *client* can use the model if real mode IS enabled.

# Let's try to instantiate and check the internal model name if possible, 
# or just print what it would use.

client = GeminiLLMClient()
print(f"Client Real Mode: {client.real_mode}")

if client.real_mode:
    print(f"Client configured model: {client.llm.model}")
    try:
        response = client.generate("System: You are a test.", "User: Say hello.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Generation failed: {e}")
else:
    print("Client is in Mock mode. To test real mode, ensure USE_REAL_LLM='gemini' and GOOGLE_API_KEY is set.")
    # Manually inspect the class to see if it picked up the config
    print(f"Configured GEMINI_MODEL_NAME: {GEMINI_MODEL_NAME}")
