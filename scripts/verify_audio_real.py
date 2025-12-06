import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt.adapter import STTAdapter
from tts.adapter import TTSAdapter

def verify_real_audio():
    load_dotenv()
    print("--- Verifying Real Audio Providers ---")
    
    # 1. Verify Configuration
    stt_provider = os.getenv("STT_PROVIDER")
    tts_provider = os.getenv("TTS_PROVIDER")
    print(f"STT_PROVIDER: {stt_provider}")
    print(f"TTS_PROVIDER: {tts_provider}")
    
    if stt_provider != "whisper" or tts_provider != "gtts":
        print("WARNING: Providers are not set to 'whisper' and 'gtts'. Check .env")

    # 2. Verify TTS (gTTS)
    print("\n[TTS] Testing gTTS...")
    try:
        tts = TTSAdapter()
        if tts.provider in ["gtts", "gTTS"]:
            path = tts.synthesize("Hello, testing real audio generation.")
            if path and os.path.exists(path):
                print(f"PASS: Audio generated at {path}")
            else:
                print("FAIL: No file generated.")
        else:
            print(f"SKIP: TTS provider is {tts.provider}")
    except Exception as e:
        print(f"FAIL: TTS Exception: {e}")

    # 3. Verify STT (Whisper)
    print("\n[STT] Testing Whisper...")
    try:
        stt = STTAdapter()
        if stt.provider == "whisper":
            # We need a small audio file to test. 
            # If TTS passed, we can use that.
            if 'path' in locals() and path and os.path.exists(path):
                print(f"Using generated TTS file for STT test: {path}")
                with open(path, "rb") as f:
                    audio_bytes = f.read()
                
                try:
                    text = stt.transcribe(audio_bytes)
                    print(f"PASS: Transcription result: '{text}'")
                except Exception as e:
                    print(f"FAIL: STT Transcription failed: {e}")
                    if "429" in str(e):
                        print("HINT: Check your OpenAI API quota.")
            else:
                print("SKIP: No audio file available to test STT.")
        else:
            print(f"SKIP: STT provider is {stt.provider}")
    except Exception as e:
        print(f"FAIL: STT Exception: {e}")

if __name__ == "__main__":
    verify_real_audio()
