import os
import pytest
from unittest.mock import patch, MagicMock
from stt.adapter import STTAdapter

def test_mock_stt_adapter():
    """Verify Mock STT Adapter returns deterministic transcript dict."""
    with patch("stt.adapter.STT_PROVIDER", "mock"):
        adapter = STTAdapter()
        result = adapter.transcribe(b"dummy_audio_bytes")
        
        assert isinstance(result, dict)
        assert "MOCK_TRANSCRIPT" in result["text"]
        assert result["provider"] == "mock"
        assert result["confidence"] == 1.0

def test_faster_whisper_lazy_import():
    """Verify Faster-Whisper mode initializes correctly (lazy import)."""
    with patch("stt.adapter.STT_PROVIDER", "faster-whisper"):
        adapter = STTAdapter()
        assert adapter.provider == "faster-whisper"
        # Should not have loaded model yet
        assert not hasattr(adapter, "_faster_whisper_model")

@pytest.mark.skipif(os.getenv("RUN_REAL_AUDIO_TESTS") != "true", reason="Skipping real audio tests")
def test_faster_whisper_transcribe_mock():
    """
    Test logic of faster-whisper path using mocks for the library.
    We mock faster_whisper.WhisperModel to avoid needing the actual model/library installed in CI.
    """
    with patch("stt.adapter.STT_PROVIDER", "faster-whisper"), \
         patch("stt.adapter.FASTER_WHISPER_MODEL", "tiny"), \
         patch("stt.adapter.AUDIO_TMP_DIR", "/tmp"), \
         patch("builtins.open", new_callable=MagicMock), \
         patch("os.remove"), \
         patch("os.path.exists", return_value=True):
        
        # Mock the import of faster_whisper
        with patch.dict("sys.modules", {"faster_whisper": MagicMock()}):
            import faster_whisper
            mock_model_cls = faster_whisper.WhisperModel
            mock_model_instance = mock_model_cls.return_value
            
            # Mock transcribe return
            MockSegment = MagicMock()
            MockSegment.text = "Hello world"
            MockInfo = MagicMock()
            MockInfo.language = "en"
            MockInfo.language_probability = 0.99
            
            mock_model_instance.transcribe.return_value = ([MockSegment], MockInfo)
            
            adapter = STTAdapter()
            result = adapter.transcribe(b"fake_audio")
            
            assert result["text"] == "Hello world"
            assert result["provider"] == "faster-whisper"
            assert result["language"] == "en"
            assert result["confidence"] == 0.99
