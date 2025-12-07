# OneCard GenAI Credit Card Assistant - System Architecture

**Reference**: FPL Technologies (OneCard) Product Builder Intern Assignment: GenAI Credit Card Assistant.pdf :contentReference[oaicite:3]{index=3}

## 1. Executive Summary
This document details the architecture for the OneCard GenAI Assistant, a multimodal (text/voice) conversational agent designed to help users manage their credit cards. The system provides instant answers to queries (e.g., "Why is my bill high?"), executes secure actions (e.g., "Block my card"), and offers financial insights. It is built on a modular, platform-agnostic architecture using FastAPI, LangChain, and Google Gemini, ensuring scalability, security, and ease of integration across Web, Mobile, and WhatsApp channels.

### Scope
- **Core Capabilities**: Intent classification, RAG-based Q&A, Action execution with human-in-the-loop confirmation, Voice-to-Text/Text-to-Speech.
- **Channels**: Web (Streamlit prototype), extensible to Mobile SDK and WhatsApp.
- **Deployment**: Containerized (Docker), cloud-ready (AWS/GCP).

---

## 2. System Overview

The architecture follows a **Microservices-based, Event-Driven** pattern (logically separated modules within a monolith for the prototype).

### High-Level Architecture Diagram

```mermaid
graph TD
    User((User)) -->|HTTP/WebSocket| APIGateway[API Gateway / Load Balancer]
    
    subgraph "Presentation Layer"
        Web[Web Client (Streamlit)]
        Mobile[Mobile App (React Native)]
        WhatsApp[WhatsApp Connector]
    end
    
    Web --> APIGateway
    Mobile --> APIGateway
    WhatsApp --> APIGateway
    
    subgraph "Application Layer (OneCard Assistant)"
        APIGateway -->|REST| API[FastAPI Service]
        
        subgraph "Orchestrator"
            API --> Agent[Assistant Agent]
            Agent --> Router[LLM Router]
            Agent --> RAG[RAG Engine]
            Agent --> Action[Action Executor]
            
            Router -->|Classify| LLM[LLM Client (Gemini)]
            RAG -->|Embed/Search| LLM
            Action -->|Tool Call| LLM
        end
        
        subgraph "Adapters"
            API --> STT[STT Adapter (Google/Whisper)]
            API --> TTS[TTS Adapter (GTTS/ElevenLabs)]
        end
    end
    
    subgraph "Data Layer"
        RAG -->|Retrieve| VectorDB[(Vector Store / Index)]
        Action -->|Read/Write| MockDB[(Mock Transaction DB)]
        Agent -->|State| SessionStore[(Redis / In-Memory)]
    end
    
    subgraph "Observability"
        Agent -->|Log| Audit[Audit Logger]
    end
```

### Component Responsibilities
1.  **API Gateway**: Entry point for all client requests. Handles rate limiting, authentication, and routing.
2.  **FastAPI Service**: Exposes REST endpoints (`/v1/messages`, `/v1/audio`) and manages request lifecycle.
3.  **Orchestrator**: The "brain" of the assistant. Manages conversation state, routes intents, and coordinates RAG vs. Action flows.
4.  **LLM Router**: Classifies user input into `Info`, `Action`, or `Ambiguous` intents using few-shot prompting.
5.  **RAG Engine**: Retrieves relevant context from the Knowledge Base to answer informational queries.
6.  **Action Executor**: Executes deterministic tools (e.g., `block_card`) with strict schema validation and user confirmation.
7.  **Data Layer**: Manages persistence for vector embeddings, mock user data, and conversation sessions.

---

## 3. Component Details

### 3.1 Interfaces & Channel Adapters
The system is designed to be channel-agnostic.
-   **Web/Mobile**: Communicate via REST API (`POST /v1/messages`). Supports text and binary audio payloads.
-   **WhatsApp**: A webhook adapter (future) maps Twilio/Meta payloads to the standard internal message schema.
-   **Voice**: `STTAdapter` abstracts the Speech-to-Text provider (Google STT, Faster Whisper). `TTSAdapter` abstracts Text-to-Speech (GTTS, ElevenLabs).

### 3.2 Orchestrator Internals
The Orchestrator (`AssistantAgent`) implements a state machine:
1.  **Input Processing**: Sanitizes input, checks for active "Action Confirmation" states.
2.  **Routing**: Calls `LLMRouter`.
    -   *Info* -> Triggers `RAG Engine`.
    -   *Action* -> Triggers `Action Executor`.
    -   *Ambiguous* -> Asks clarifying question.
3.  **Response Generation**: Synthesizes final response using LLM + Tool Output/RAG Context.

### 3.3 Knowledge & Data Layer
-   **Knowledge Base**: Text-based source of truth (`data/knowledge_base.txt`) containing policy documents.
-   **Vector Store**: Local FAISS/Chroma-style index (JSON-based for prototype) storing embeddings.
-   **Mock DB**: JSON file (`data/mock_db.json`) simulating a core banking system.
-   **Session Store**: Abstracted key-value store. Defaults to in-memory, production-ready for Redis.

### 3.4 LLM & Tooling Abstractions
-   **`function_schema.py`**: Pydantic models defining tool inputs (e.g., `BlockCardRequest`).
-   **`tool_descriptions.md`**: Natural language descriptions for the LLM to understand tool capabilities.
-   **`GeminiLLMClient`**: Wrapper around Google Generative AI, handling retries and fallback to mock mode.

---

## 4. Data Flows

### Flow 1: Informational RAG Query ("Why is my bill high?")
1.  **User** sends text: "Why is my bill high?"
2.  **Router** classifies as `Info` (Confidence: 0.95).
3.  **Agent** calls `RAG Engine`.
4.  **RAG** embeds query, searches Vector Store for "bill", "charges", "high".
5.  **Retrieval**: Returns chunks about "Late payment fees", "Forex markup".
6.  **Synthesis**: LLM generates answer citing retrieved chunks.
7.  **Response**: "Your bill might include late payment charges (2.5%) or forex markup (1%)..."

### Flow 2: Action Execution ("Block my card")
1.  **User** sends text: "Block my card".
2.  **Router** classifies as `Action` (`block_card`).
3.  **Agent** checks `requires_confirmation` for `block_card`.
4.  **Agent** returns: "Are you sure? Reply YES to confirm." (State: `WAITING_CONFIRMATION`).
5.  **User** replies: "YES".
6.  **Agent** verifies confirmation.
7.  **Action Executor** calls `block_card(user_id)`.
8.  **Mock DB** updates `card_status` to `blocked`.
9.  **Audit** logs event: `Action: block_card, User: 12345, Status: Success`.
10. **Response**: "Card blocked successfully."

### Flow 3: Voice to Action
1.  **User** sends audio blob.
2.  **STT Adapter** transcribes audio to text: "Freeze my card".
3.  **Router** classifies "Freeze my card" as `Action` (`block_card`).
4.  **Flow** proceeds as Flow 2.
5.  **Response** text is sent to **TTS Adapter**.
6.  **TTS** generates audio file.
7.  **API** returns text + audio URL.

---

## 5. API Contract

### `POST /v1/sessions`
Initialize a new conversation session.
```json
// Request
{ "user_id": "user_123", "client_type": "web" }

// Response
{ "session_id": "sess_abc123", "status": "active" }
```

### `POST /v1/messages`
Send a message (text) to the assistant.
```json
// Request
{
  "session_id": "sess_abc123",
  "text": "What is my balance?"
}

// Response
{
  "response_text": "Your current balance is ₹45,000.",
  "audio_url": null,
  "actions_taken": ["get_account_summary"]
}
```

---

## 6. Non-Functional Requirements (NFRs)

-   **Latency**:
    -   Text-to-Text: < 2 seconds (p95).
    -   Voice-to-Audio: < 5 seconds (p95).
-   **Throughput**: Prototype supports 10 concurrent users. Production target: 1000 RPS (horizontally scalable).
-   **Storage**:
    -   Embeddings: ~1KB per chunk. 1M documents ~= 1GB vector index.
    -   Session Store: ~10KB per active session.
-   **Availability**: 99.9% uptime (stateless API + Redis replication).

---

## 7. Security & Privacy

-   **Authentication**: API calls require `Authorization: Bearer <token>` (JWT).
-   **Secrets Management**: All API keys (Gemini, Twilio) stored in `.env`, injected at runtime. No hardcoded secrets.
-   **PII Handling**:
    -   Logs: PII (names, card numbers) masked in audit logs.
    -   Storage: Mock DB uses synthetic data. Production DB would be encrypted at rest.
-   **Audit Trail**: All sensitive actions (Block, Unblock) are immutably logged to `audit_log.jsonl` (or SIEM).

---

## 8. Failure Modes & Mitigation

| Failure Scenario | Mitigation Strategy |
| :--- | :--- |
| **LLM Down/Timeout** | Fallback to "Mock Mode" or canned response ("I'm having trouble connecting..."). |
| **STT Failure** | Return error "Could not understand audio, please type." |
| **Action Failure** | Atomic transactions. If DB update fails, rollback and notify user. |
| **High Load** | API Gateway rate limiting (429 Too Many Requests). |

---

## 9. Observability & Testing

-   **Metrics**: Request latency, Error rate, LLM token usage, Active sessions.
-   **Logs**: Structured JSON logs with `trace_id` for request correlation.
-   **Testing Strategy**:
    -   **Unit Tests**: `pytest` for individual components (Router, RAG).
    -   **Integration Tests**: End-to-end flows using `TestClient`.
    -   **Smoke Tests**: `scripts/run_local.sh` for environment validation.

---

## 10. Scalability & Future-Proofing

-   **Multi-LLM Support**: The `LLMClient` abstraction allows swapping Gemini for GPT-4 or local Llama 3 without code changes.
-   **RAG Evolution**: The `RAG Engine` can migrate from local JSON index to Pinecone/Milvus for billion-scale retrieval.
-   **Channel Expansion**: New adapters (e.g., Slack, Telegram) can be added by implementing the `ChannelAdapter` interface.

---

## 11. Appendix: Requirement Mapping

| Requirement (PDF) | Section in Doc |
| :--- | :--- |
| **System Architecture Diagram** | 2. System Overview |
| **Component Details** | 3. Component Details |
| **Data Flow Diagrams** | 4. Data Flows |
| **API Contract** | 5. API Contract |
| **Security & Privacy** | 7. Security & Privacy |
| **Scalability** | 10. Scalability |
| **Observability** | 9. Observability & Testing |

---

## 12. Demo Script (10-min Presentation)

1.  **Intro (1 min)**: "Hi, I'm [Name]. I built the OneCard GenAI Assistant to solve the problem of complex financial queries."
2.  **Architecture (2 mins)**: Show **High-Level Diagram**. Explain the modular design (Router -> RAG/Action).
3.  **Live Demo (4 mins)**:
    -   Show "Why is my bill high?" (RAG).
    -   Show "Block my card" (Action + Confirmation).
    -   Show Voice interaction (if enabled).
4.  **Deep Dive (2 mins)**: Explain the **LLM Router** logic and **Safety Mechanisms** (Confirmation flow).
5.  **Future & Q&A (1 min)**: Mention Scalability (Redis/Vector DB) and Mobile SDK.
