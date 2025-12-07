import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts.adapter import TTSAdapter

def verify_gtts():
    load_dotenv()
    print("--- Verifying gTTS Provider ---")
    
    tts_provider = os.getenv("TTS_PROVIDER")
    print(f"TTS_PROVIDER: {tts_provider}")
    
    if tts_provider != "gtts":
        print("FAIL: TTS_PROVIDER is not gtts")
        return

    tts = TTSAdapter()
    text = "Hello, this is a test of the Google Text to Speech provider."
    
    print(f"Synthesizing: '{text}'")
    try:
        output_path = tts.synthesize(text)
        if output_path and os.path.exists(output_path):
            print(f"PASS: Audio generated at {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print("FAIL: No output file generated.")
            
    except Exception as e:
        print(f"FAIL: Exception: {e}")

if __name__ == "__main__":
    verify_gtts()
