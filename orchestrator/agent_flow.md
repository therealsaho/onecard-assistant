# Agent Flow

This document describes the runtime flow of the OneCard Assistant.

## Flow Steps

1.  **Receive Input**
    - The system receives text input from the user (or transcribed audio).

2.  **Router Classification**
    - The `ROUTER_PROMPT` analyzes the input to determine `intent` and `action_type`.

3.  **Intent Handling**

    -   **Case A: Intent = `info`**
        1.  Check if the query requires specific user data (e.g., "my balance") or general policy info (e.g., "forex fee").
        2.  If **User Data**: Call the relevant tool (e.g., `get_account_summary`) and format the response.
        3.  If **Policy Info**: Call the RAG module to search `knowledge_base.txt`.
            -   Format the answer using `RAG_PROMPT`.
            -   Include the citation: "Policy source: knowledge_base.txt (line X)".

    -   **Case B: Intent = `action`**
        1.  Identify the target tool (e.g., `block_card`).
        2.  **Check Preconditions**:
            -   If the tool requires confirmation (like `block_card`):
                -   Check if the user has already confirmed (context check).
                -   If NOT confirmed, send the `CONFIRMATION_PROMPT` to the user.
                -   **STOP** and wait for user response.
                -   If user replies "YES", proceed to step 3.
                -   If user replies anything else, cancel and notify user.
        3.  **Execute Tool**: Call the tool with extracted parameters.
        4.  **Audit**: Log the action (timestamp, user_id, action, result).
        5.  **Response**: Return a human-friendly success message with any relevant IDs (e.g., "Card blocked. Confirmation ID: blk_999").

    -   **Case C: Intent = `ambiguous`**
        1.  Ask a clarifying question.
        2.  Example: "I'm not sure if you want to check your balance or block your card. Could you clarify?"

4.  **Fallback**
    -   If the system encounters an error or the user requests human help:
    -   "If you want to speak to a human, contact support at 1800-XXX-XXXX."
