import os
import pytest
from unittest.mock import patch
from stt.adapter import STTAdapter
from tts.adapter import TTSAdapter
from orchestrator.agent import AssistantAgent

def test_mock_stt_adapter():
    """Verify Mock STT Adapter returns deterministic transcript."""
    with patch("stt.adapter.STT_PROVIDER", "mock"):
        adapter = STTAdapter()
        transcript = adapter.transcribe(b"dummy_audio_bytes")
        assert "MOCK_TRANSCRIPT" in transcript

def test_mock_tts_adapter():
    """Verify Mock TTS Adapter returns a file path."""
    with patch("tts.adapter.TTS_PROVIDER", "mock"):
        adapter = TTSAdapter()
        path = adapter.synthesize("Hello world")
        assert path is not None
        assert os.path.exists(path)
        # Cleanup
        if os.path.exists(path):
            os.remove(path)

def test_e2e_mock_audio_flow():
    """Verify E2E flow: Audio -> STT -> Agent -> TTS -> Audio Path."""
    # Setup Mocks
    with patch("stt.adapter.STT_PROVIDER", "mock"), \
         patch("tts.adapter.TTS_PROVIDER", "mock"):
        
        stt = STTAdapter()
        tts = TTSAdapter()
        agent = AssistantAgent()
        session_state = {}
        
        # 1. Transcribe
        audio_input = b"fake_audio"
        transcript = stt.transcribe(audio_input)
        assert "MOCK_TRANSCRIPT" in transcript
        
        # 2. Agent Turn
        # We'll just use the transcript as user input
        response = agent.handle_turn("user_audio_test", transcript, session_state)
        response_text = response["response_text"]
        assert response_text is not None
        
        # 3. Synthesize
        audio_path = tts.synthesize(response_text)
        assert audio_path is not None
        assert os.path.exists(audio_path)
        
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
