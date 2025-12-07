import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"RUN_REAL_EMBEDDINGS: {os.getenv('RUN_REAL_EMBEDDINGS')}")
print(f"GOOGLE_API_KEY present: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("langchain_google_genai imported successfully.")
except ImportError as e:
    print(f"Failed to import langchain_google_genai: {e}")
    sys.exit(1)

from llm.gemini_client import GeminiLLMClient

client = GeminiLLMClient()
print(f"Client Real Mode: {client.real_mode}")

if client.real_mode:
    text = "test embedding"
    vector = client.embed(text)
    print(f"Embedding length: {len(vector)}")
    print(f"First 5 dims: {vector[:5]}")
    
    is_zero = all(v == 0.0 for v in vector)
    print(f"Is zero vector: {is_zero}")
else:
    print("Client is in Mock Mode.")
