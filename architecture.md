# Architecture

```mermaid
graph LR
    User((User)) --> Frontend[Streamlit Frontend]
    Frontend --> API[API Gateway (Text/Audio)]
    API --> Orchestrator[Orchestrator (Router / RAG / Action Module)]
    Orchestrator --> KB[(Knowledge Base (txt))]
    Orchestrator --> DB[(Mock DB (json))]
    
    subgraph Data Layer
        KB
        DB
    end
```

**Data Flows:**
1. **User Query** -> **Frontend** -> **API Gateway** -> **Orchestrator**
2. **Orchestrator** -> **Router** -> decides between **RAG** (Knowledge Base) or **Action** (Mock DB)
3. **Response** -> **Orchestrator** -> **API Gateway** -> **Frontend** -> **User**
