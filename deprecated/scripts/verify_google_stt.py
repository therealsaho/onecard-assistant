import os
import sys
import wave
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt.adapter import STTAdapter

def create_dummy_wav(filename):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        # Write 1 second of silence
        wav_file.writeframes(b'\x00' * 44100 * 2)

def verify_google_stt():
    load_dotenv()
    print("--- Verifying Google STT Provider ---")
    
    stt_provider = os.getenv("STT_PROVIDER")
    print(f"STT_PROVIDER: {stt_provider}")
    
    if stt_provider != "google":
        print("FAIL: STT_PROVIDER is not google")
        return

    stt = STTAdapter()
    
    # Create dummy wav
    wav_path = "dummy_test.wav"
    create_dummy_wav(wav_path)
    
    try:
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()
            
        print("Transcribing dummy WAV (silence)...")
        result = stt.transcribe(audio_bytes)
        print(f"Result: {result}")
        
        if result["provider"] == "google":
            print("PASS: Provider is google")
            if "Could not understand" in result["text"] or "Error" not in result["text"]:
                print("PASS: API call likely succeeded (even if silence)")
            else:
                print(f"WARN: Unexpected text: {result['text']}")
        else:
            print(f"FAIL: Provider mismatch: {result['provider']}")
            
    except Exception as e:
        print(f"FAIL: Exception: {e}")
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

if __name__ == "__main__":
    verify_google_stt()
