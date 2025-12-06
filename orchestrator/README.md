# Orchestrator Design

This directory contains the design and configuration for the OneCard Assistant's LLM orchestration layer.

## Overview
The orchestrator acts as the central brain, routing user intents to either the RAG module (for information) or the Action module (for account operations). It enforces security policies, requires confirmation for destructive actions, and ensures consistent persona behavior.

## Security Assumptions
1.  **Authenticated Session**: The agent operates within an authenticated user session.
2.  **User Context**: A valid `user_id` is available in the context for all tool calls.
3.  **Secure Channel**: Communication between the user and the agent is over a secure channel.

## Runtime Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Orchestrator
    participant Router
    participant RAG
    participant Tools
    participant DB

    User->>Frontend: "Block my card"
    Frontend->>Orchestrator: Input Text
    Orchestrator->>Router: Classify Intent
    Router-->>Orchestrator: {intent: "action", action_type: "block_card"}
    
    alt Action requires confirmation
        Orchestrator->>Frontend: "Are you sure? Reply YES to confirm."
        User->>Frontend: "YES"
        Frontend->>Orchestrator: "YES"
        Orchestrator->>Tools: block_card(user_id, reason="User Request")
        Tools->>DB: Update card_status
        Tools-->>Orchestrator: Success + Audit Log
        Orchestrator->>Frontend: "Card blocked. Confirmation ID: ..."
    else Info Query
        User->>Frontend: "What is the forex markup?"
        Frontend->>Orchestrator: Input Text
        Orchestrator->>Router: Classify Intent
        Router-->>Orchestrator: {intent: "info"}
        Orchestrator->>RAG: Search Knowledge Base
        RAG-->>Orchestrator: "1% markup (Source: knowledge_base.txt)"
        Orchestrator->>Frontend: Answer with citation
    end
```
