from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import os
import sys

# Add root to path to import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.agent import AssistantAgent
from api.schemas import (
    SessionCreateRequest, SessionCreateResponse,
    MessageRequest, MessageResponse,
    TranscribeResponse,
    ConfirmRequest, OTPRequest,
    TTSRequest, TTSResponse
)
from api.session_store import SessionStore, InMemorySessionStore
from adapters.stt_adapter import STTAdapter
from adapters.tts_adapter import TTSAdapter

app = FastAPI(title="OneCard Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
session_store = InMemorySessionStore()
assistant = AssistantAgent()
stt_adapter = STTAdapter()
tts_adapter = TTSAdapter()

def get_session_store():
    return session_store

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/v1/sessions", response_model=SessionCreateResponse)
def create_session(request: SessionCreateRequest, store: SessionStore = Depends(get_session_store)):
    session_id = store.create_session(request.user_id, request.client_type, request.metadata)
    return SessionCreateResponse(
        session_id=session_id,
        user_id=request.user_id,
        created_at=store.get_session(session_id)["created_at"]
    )

@app.post("/v1/messages", response_model=MessageResponse)
def send_message(request: MessageRequest, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Get session state
    session_state = session.get("state", {})
    
    # Call Agent
    # Note: handle_turn signature is (user_id, user_message, session_state)
    # It returns a dict with response_text, tool_output, debug_info, and updates session_state in place (or returns it?)
    # Let's check agent.py signature.
    # Based on previous context: handle_turn(self, user_id: str, user_message: str, session_state: Dict[str, Any]) -> Dict[str, Any]
    
    try:
        response = assistant.handle_turn(session["user_id"], request.text, session_state)
        
        # Update session state persistence
        store.update_session(request.session_id, {"state": session_state})
        
        return MessageResponse(
            response_text=response.get("response_text", ""),
            tool_output=response.get("tool_output"),
            debug_info=response.get("debug_info")
        )
    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/audio/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = stt_adapter.transcribe(contents)
        return TranscribeResponse(
            text=result["text"],
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

@app.post("/v1/actions/confirm", response_model=MessageResponse)
def confirm_action(request: ConfirmRequest, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session_state = session.get("state", {})
    
    # To confirm, we treat it as a message. The agent handles state.
    # "yes" or "no"
    try:
        response = assistant.handle_turn(session["user_id"], request.confirmation, session_state)
        store.update_session(request.session_id, {"state": session_state})
        
        return MessageResponse(
            response_text=response.get("response_text", ""),
            tool_output=response.get("tool_output"),
            debug_info=response.get("debug_info")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/actions/otp", response_model=MessageResponse)
def submit_otp(request: OTPRequest, store: SessionStore = Depends(get_session_store)):
    session = store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session_state = session.get("state", {})
    
    # OTP is also just a message in the current agent flow
    try:
        response = assistant.handle_turn(session["user_id"], request.otp, session_state)
        store.update_session(request.session_id, {"state": session_state})
        
        return MessageResponse(
            response_text=response.get("response_text", ""),
            tool_output=response.get("tool_output"),
            debug_info=response.get("debug_info")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/audio/synthesize", response_model=TTSResponse)
def synthesize_audio(request: TTSRequest):
    try:
        result = tts_adapter.synthesize(request.text)
        return TTSResponse(
            audio_path=result["audio_path"],
            duration=result.get("duration")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
