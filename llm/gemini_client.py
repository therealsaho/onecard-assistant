"""
Gemini LLM Client module.
Wraps LangChain's ChatGoogleGenerativeAI for real mode, and provides a mock fallback.
"""
import os
from config.llm_settings import USE_REAL_LLM, GOOGLE_API_KEY, GEMINI_MODEL_NAME

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class GeminiLLMClient:
    """
    Client for interacting with Gemini Flash via LangChain, or falling back to mock.
    """
    
    def __init__(self):
        self.real_mode = USE_REAL_LLM
        
        if self.real_mode:
            if not GOOGLE_API_KEY:
                print("Warning: USE_REAL_LLM is 'gemini' but GOOGLE_API_KEY is missing. Falling back to mock.")
                self.real_mode = False
            elif not LANGCHAIN_AVAILABLE:
                print("Warning: USE_REAL_LLM is 'gemini' but langchain-google-genai is not installed. Falling back to mock.")
                self.real_mode = False
            else:
                self.llm = ChatGoogleGenerativeAI(
                    model=GEMINI_MODEL_NAME,
                    temperature=0.0,
                    google_api_key=GOOGLE_API_KEY,
                    convert_system_message_to_human=True # Sometimes needed for older LC versions, safe to keep
                )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response using Gemini Flash (real) or a mock template (mock).
        
        Args:
            system_prompt: The system instruction.
            user_prompt: The user's input or context.
            
        Returns:
            The generated text response.
        """
        if not self.real_mode:
            # Safe fallback: Mock Mode
            # Return a deterministic string based on input length or content to simulate "processing"
            return f"MOCK_LLM_RESPONSE: {user_prompt[:80]}..."
            
        try:
            # Real Mode: Call Gemini
            messages = [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"
