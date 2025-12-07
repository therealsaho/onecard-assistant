# OneCard GenAI Credit Card Assistant  
A multimodal (text + voice) intelligent assistant that answers credit-card queries and performs secure actions such as blocking a card, checking transactions, creating EMIs, and more.  
Built as part of the **FPL Technologies (OneCard) GenAI Product Builder Assignment**.

---

##  Features

### 1. Information Retrieval
- RAG-based answers from OneCard policies  
- Semantic search over the knowledge base  
- LLM-powered synthesis (Gemini)

### 2. Action Execution
- Deterministic tool layer with strict Pydantic schemas  
- Mandatory confirmation for destructive actions  
- Mock API execution for:  
  - Block/Unblock card    
  - EMI creation    
  - Transaction lookup    
  - Bill & Statement retrieval  

### 3. Multimodal Experience
- **STT**: Google / Whisper (audio → text)  
- **TTS**: gTTS (text → audio)  
- Streamlit UI for live demo  

---

##  Architecture Overview
Full architecture is documented in:
- `docs/architecture.md`  
- `docs/diagrams/` (high-level + orchestrator diagrams)

System includes:
- API Gateway  
- FastAPI backend  
- Orchestrator (Agent, Router, RAG Engine, Tool Executor)  
- Vector Store, Mock Database, Session Store  
- LLM Client (Gemini)  
- Audit + Observability layer  

---

##  Running Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy `.env.example` → `.env` and set:
```bash
GEMINI_API_KEY=your_key
GOOGLE_API_KEY=your_key
```

### 3. Build RAG index
```bash
python onecard/scripts/build_rag_index.py
```

### 4. Start API backend
```bash
uvicorn onecard.api.app:app --reload
```

### 5. Launch Streamlit UI
```bash
streamlit run onecard/ui/app.py
```

## Testing
```bash
pytest -q
```

##  Demo & Walkthrough
Demo video: add link here

Demo script: `docs/DEMO_INSTRUCTIONS.md`


## Author
Sanjeev Hotha
