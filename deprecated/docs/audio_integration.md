# Audio Integration Guide

The OneCard Assistant Prototype supports modular Speech-to-Text (STT) and Text-to-Speech (TTS) adapters.

## Configuration

Audio settings are managed in `config/audio_settings.py` and environment variables.

### Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `STT_PROVIDER` | `mock` | STT Provider: `mock` or `whisper` |
| `TTS_PROVIDER` | `mock` | TTS Provider: `mock` or `gtts` |
| `OPENAI_API_KEY` | - | Required if `STT_PROVIDER=whisper` |
| `UPLOAD_MAX_SIZE_MB` | `5` | Max audio upload size in MB |
| `AUDIO_TMP_DIR` | `./tmp_audio` | Directory for temporary audio files |

## Adapters

### STT Adapter (`stt/adapter.py`)
- **Mock Mode**: Returns a fixed transcript ("MOCK_TRANSCRIPT...").
- **Whisper Mode**: Uses OpenAI's Whisper API (requires `openai` package and API key).

### TTS Adapter (`tts/adapter.py`)
- **Mock Mode**: Generates a placeholder audio file.
- **gTTS Mode**: Uses Google Text-to-Speech (requires `gTTS` package).

## Usage

1. **Mock Mode (Default)**:
   - Just run the app: `python -m streamlit run ui/app.py`
   - Upload any audio file to see the mock transcript.
   - Enable "Play audio replies" to hear the mock audio response.

2. **Real Mode**:
   - Install dependencies: `pip install openai gTTS`
   - Set environment variables:
     ```bash
     export STT_PROVIDER=whisper
     export TTS_PROVIDER=gtts
     export OPENAI_API_KEY=your_key_here
     ```
   - Run the app.
