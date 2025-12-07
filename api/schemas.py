from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    user_id: str = Field(..., description="Unique identifier for the user", example="user_123")
    client_type: str = Field("web", description="Client type (web, mobile, whatsapp)", example="web")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")

class SessionCreateResponse(BaseModel):
    """Response for session creation."""
    session_id: str = Field(..., description="Unique session ID")
    user_id: str
    created_at: float

class MessageRequest(BaseModel):
    """Request to send a message to the assistant."""
    session_id: str = Field(..., description="Active session ID")
    text: str = Field(..., description="User message text", example="What is my balance?")

class MessageResponse(BaseModel):
    """Response from the assistant."""
    response_text: str = Field(..., description="Assistant's text response")
    tool_output: Optional[Any] = Field(None, description="Output from any tool execution")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information if enabled")

class TranscribeResponse(BaseModel):
    """Response for audio transcription."""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(0.0, description="Transcription confidence score")

class ConfirmRequest(BaseModel):
    """Request to confirm a pending action."""
    session_id: str = Field(..., description="Active session ID")
    confirmation: str = Field(..., description="User confirmation (yes/no)", example="yes")

class OTPRequest(BaseModel):
    """Request to submit an OTP."""
    session_id: str = Field(..., description="Active session ID")
    otp: str = Field(..., description="OTP code", example="123456")

class TTSRequest(BaseModel):
    """Request for text-to-speech."""
    text: str = Field(..., description="Text to synthesize")

class TTSResponse(BaseModel):
    """Response for text-to-speech."""
    audio_path: str = Field(..., description="Path to generated audio file")
    duration: Optional[float] = Field(None, description="Duration in seconds")
