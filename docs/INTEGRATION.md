# OneCard Assistant API Integration Guide

The OneCard Assistant now exposes a platform-agnostic HTTP API. This allows you to integrate the assistant with various channels (Web, WhatsApp, Mobile App) without modifying the core logic.

## Base URL
Local: `http://localhost:8000`

## Endpoints

### 1. Create Session
**POST** `/v1/sessions`
Creates a new session for a user.

**Request:**
```json
{
  "user_id": "user_123",
  "client_type": "web",
  "metadata": {"device": "mobile"}
}
```

**Response:**
```json
{
  "session_id": "sess_user_123_1700000000",
  "user_id": "user_123",
  "created_at": 1700000000.0
}
```

### 2. Send Message
**POST** `/v1/messages`
Sends a text message to the assistant.

**Request:**
```json
{
  "session_id": "sess_user_123_...",
  "text": "What is my balance?"
}
```

**Response:**
```json
{
  "response_text": "Your current balance is $1,250.00.",
  "tool_output": null,
  "debug_info": null
}
```

### 3. Transcribe Audio
**POST** `/v1/audio/transcribe`
Uploads an audio file for transcription.

**Request:**
`multipart/form-data` with field `file`.

**Response:**
```json
{
  "text": "What is my balance?",
  "confidence": 0.95
}
```

### 4. Confirm Action
**POST** `/v1/actions/confirm`
Confirms a sensitive action (e.g., blocking a card).

**Request:**
```json
{
  "session_id": "sess_user_123_...",
  "confirmation": "yes"
}
```

### 5. Submit OTP
**POST** `/v1/actions/otp`
Submits an OTP code.

**Request:**
```json
{
  "session_id": "sess_user_123_...",
  "otp": "123456"
}
```

### 6. Text-to-Speech
**POST** `/v1/audio/synthesize`
Synthesizes text to audio.

**Request:**
```json
{
  "text": "Hello world"
}
```

**Response:**
```json
{
  "audio_path": "path/to/audio.mp3",
  "duration": 1.5
}
```

## Example: Web Integration (JavaScript)

```javascript
async function chat() {
  // 1. Create Session
  const sessionRes = await fetch('http://localhost:8000/v1/sessions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: 'web_user', client_type: 'web'})
  });
  const session = await sessionRes.json();
  
  // 2. Send Message
  const msgRes = await fetch('http://localhost:8000/v1/messages', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      session_id: session.session_id,
      text: 'What is my balance?'
    })
  });
  const reply = await msgRes.json();
  console.log('Assistant:', reply.response_text);
}
```
