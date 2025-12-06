"""
TTS Adapter module.
"""
import os
import time
from typing import Union
from config.audio_settings import TTS_PROVIDER, AUDIO_TMP_DIR

class TTSAdapter:
    """
    Adapter for Text-to-Speech services.
    """
    def __init__(self):
        self.provider = TTS_PROVIDER
        
    def synthesize(self, text: str) -> Union[str, bytes, None]:
        """
        Synthesizes text to audio.
        
        Args:
            text: The text to convert to speech.
            
        Returns:
            File path (str) to the generated audio file.
        """
        if not text:
            return None

        timestamp = int(time.time())
        
        if self.provider == "mock":
            # Return a placeholder file
            output_path = os.path.join(AUDIO_TMP_DIR, f"mock_tts_{timestamp}.mp3")
            with open(output_path, "wb") as f:
                # Minimal valid MP3 frame or just dummy bytes? 
                # Streamlit might complain if it's not valid audio. 
                # Let's write a few dummy bytes.
                f.write(b"MOCK_AUDIO_BYTES_PLACEHOLDER")
            return output_path
            
        if self.provider in ["gtts", "gTTS"]:
            try:
                from gtts import gTTS
                
                # Clean up old files in tmp dir to prevent bloat (simple heuristic)
                # ... (omitted for brevity, but good practice)
                
                tts = gTTS(text=text, lang='en')
                output_path = os.path.join(AUDIO_TMP_DIR, f"tts_{timestamp}.mp3")
                tts.save(output_path)
                return output_path
                
            except ImportError:
                print("gTTS not installed. Falling back to mock behavior.")
                # Fallback
                output_path = os.path.join(AUDIO_TMP_DIR, f"fallback_tts_{timestamp}.mp3")
                with open(output_path, "wb") as f:
                    f.write(b"FALLBACK_AUDIO")
                return output_path
            except Exception as e:
                print(f"TTS Error: {e}")
                return None
                
        return None
