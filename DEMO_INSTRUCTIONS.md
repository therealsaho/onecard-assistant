# Demo Instructions

## Setup
1.  **Environment**:
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Run App (Mock Mode)**:
    ```bash
    # PowerShell
    $env:USE_REAL_LLM="false"
    streamlit run ui/app.py
    ```

## Demo Script

### Flow 1: Info Query
**User**: "Why is my bill high?"
**Expected**: Agent retrieves account summary (balance, due date) and displays it.

### Flow 2: Policy Query (RAG)
**User**: "What's the forex markup?"
**Expected**: Agent searches knowledge base and answers "1% markup" with a citation.

### Flow 3: Action + Confirmation
**User**: "Block my card"
**Expected**:
1.  Agent asks: "Are you sure you want to block your card immediately? Reply with the single word **YES**..."
2.  UI shows "Confirmation Required".
**User**: "YES"
**Expected**:
1.  Agent confirms: "Action confirmed. Card blocked successfully."
2.  UI shows "Audit Logged".
3.  Debug panel shows audit event.

### Flow 4: Action Cancellation (Optional)
**User**: "Block my card"
**User**: "No wait"
**Expected**: Agent says "Action cancelled."
