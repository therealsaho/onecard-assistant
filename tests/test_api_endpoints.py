import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.app import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_session():
    response = client.post("/v1/sessions", json={
        "user_id": "test_user",
        "client_type": "web",
        "metadata": {"foo": "bar"}
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["user_id"] == "test_user"
    return data["session_id"]

def test_send_message():
    session_id = test_create_session()
    
    response = client.post("/v1/messages", json={
        "session_id": session_id,
        "text": "Hello"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response_text" in data
    # Agent usually responds to Hello
    
def test_transcribe_audio():
    # Mock audio file
    response = client.post("/v1/audio/transcribe", files={
        "file": ("test.wav", b"fake audio bytes", "audio/wav")
    })
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "confidence" in data

def test_synthesize_audio():
    response = client.post("/v1/audio/synthesize", json={
        "text": "Hello world"
    })
    assert response.status_code == 200
    data = response.json()
    assert "audio_path" in data

def test_block_card_flow():
    # Test safety: block card should require confirmation
    session_id = test_create_session()
    
    # 1. Request block
    response = client.post("/v1/messages", json={
        "session_id": session_id,
        "text": "Block my card"
    })
    assert response.status_code == 200
    data = response.json()
    # Should ask for confirmation
    assert "confirm" in data["response_text"].lower() or "sure" in data["response_text"].lower()
    
    # 2. Confirm
    response = client.post("/v1/actions/confirm", json={
        "session_id": session_id,
        "confirmation": "yes"
    })
    assert response.status_code == 200
    data = response.json()
    # Should be blocked
    assert "blocked" in data["response_text"].lower()
