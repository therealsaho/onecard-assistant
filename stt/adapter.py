"""
STT Adapter module.
"""
import os
from typing import Optional
from config.audio_settings import STT_PROVIDER

class STTAdapter:
    """
    Adapter for Speech-to-Text services.
    """
    def __init__(self):
        self.provider = STT_PROVIDER
        
    def transcribe(self, audio_bytes: bytes) -> dict:
        """
        Transcribes audio bytes to text.
        
        Args:
            audio_bytes: The audio file content in bytes.
            
        Returns:
            A dictionary containing:
            - text: The transcribed text.
            - provider: The provider used.
            - language: Detected language (if available).
            - confidence: Confidence score (if available).
            
        Raises:
            ValueError: If provider configuration is invalid (e.g. missing keys).
        """
        if self.provider == "mock":
            return {
                "text": "MOCK_TRANSCRIPT: This is a simulated voice command.",
                "provider": "mock",
                "language": "en",
                "confidence": 1.0
            }
        
        if self.provider == "faster-whisper":
            try:
                from faster_whisper import WhisperModel
                from config.audio_settings import FASTER_WHISPER_MODEL, AUDIO_TMP_DIR
                import uuid
                
                # Save audio bytes to temp file
                temp_filename = f"stt_{uuid.uuid4()}.wav"
                temp_path = os.path.join(AUDIO_TMP_DIR, temp_filename)
                
                with open(temp_path, "wb") as f:
                    f.write(audio_bytes)
                
                try:
                    # Load model (lazy loading could be better, but for now per-request or cached in class)
                    # Ideally, we should cache the model instance in the class or a global singleton
                    if not hasattr(self, "_faster_whisper_model"):
                        # Run on CPU with INT8 for compatibility/speed on standard machines
                        self._faster_whisper_model = WhisperModel(FASTER_WHISPER_MODEL, device="cpu", compute_type="int8")
                    
                    segments, info = self._faster_whisper_model.transcribe(temp_path, beam_size=5)
                    
                    # Aggregate segments
                    text = " ".join([segment.text for segment in segments]).strip()
                    
                    return {
                        "text": text,
                        "provider": "faster-whisper",
                        "language": info.language,
                        "confidence": info.language_probability
                    }
                    
                finally:
                    # Cleanup
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except ImportError:
                raise ImportError("faster-whisper package is required. Please install it: pip install faster-whisper")
            except Exception as e:
                raise RuntimeError(f"Faster-Whisper Error: {str(e)}") from e

        if self.provider == "whisper":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                 raise ValueError("OPENAI_API_KEY not found for Whisper provider.")
            
            try:
                from openai import OpenAI
                import io
                
                client = OpenAI(api_key=api_key)
                
                # Create a file-like object
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.mp3" 
                
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                return {
                    "text": transcript.text,
                    "provider": "whisper",
                    "language": "unknown", # OpenAI API doesn't always return this easily in simple call
                    "confidence": None
                }
                
            except ImportError:
                raise ImportError("openai package is required for Whisper STT. Please install it.")
            except Exception as e:
                raise RuntimeError(f"Whisper Error: {str(e)}") from e
            
        if self.provider == "google":
            try:
                import speech_recognition as sr
                import io
                
                # SpeechRecognition expects a file path or file-like object
                # It supports WAV, AIFF, FLAC. MP3 requires conversion (e.g. pydub) which needs ffmpeg.
                # For this prototype, we'll assume WAV or try to process.
                
                r = sr.Recognizer()
                
                # Create a file-like object
                audio_file = io.BytesIO(audio_bytes)
                
                # We need to know the format. If it's bytes, SR might struggle if it's not a standard container.
                # Let's try to write to a temp wav file if possible, or just pass the bytesIO if it's WAV.
                # Since we don't know if it's MP3 or WAV from bytes alone easily without inspection,
                # we'll try to treat it as WAV first.
                
                try:
                    with sr.AudioFile(audio_file) as source:
                        audio_data = r.record(source)
                        text = r.recognize_google(audio_data)
                        return {
                            "text": text,
                            "provider": "google",
                            "language": "en-US", # Google API defaults to en-US usually unless specified
                            "confidence": 0.0 # Google API doesn't always return confidence in simple mode
                        }
                except ValueError: 
                    # This often happens if file format is not supported (e.g. MP3 without ffmpeg)
                    return {
                        "text": "Error: Audio format not supported. Please upload WAV files for Google STT.",
                        "provider": "google",
                        "language": "error",
                        "confidence": 0.0
                    }
                except sr.UnknownValueError:
                    return {
                        "text": "Error: Could not understand audio.",
                        "provider": "google",
                        "language": "error",
                        "confidence": 0.0
                    }
                except sr.RequestError as e:
                    return {
                        "text": f"Error: Google API request failed: {e}",
                        "provider": "google",
                        "language": "error",
                        "confidence": 0.0
                    }
                    
            except ImportError:
                raise ImportError("SpeechRecognition package is required. Please install it: pip install SpeechRecognition")
            except Exception as e:
                raise RuntimeError(f"Google STT Error: {str(e)}") from e

        return {
            "text": f"Error: Unknown STT provider: {self.provider}",
            "provider": "error",
            "language": "unknown",
            "confidence": 0.0
        }
