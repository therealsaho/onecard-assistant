# Event Flow

## Main Event Loop

1.  **User Input Event**
    -   Trigger: User clicks "Send" or presses Enter.
    -   Action:
        1.  Append user message to `session_state.messages`.
        2.  Render user message immediately.
        3.  Show spinner "Processing...".
        4.  Call `orchestrator.process_user_input(text)`.

2.  **Orchestrator Response Event**
    -   Trigger: `process_user_input` returns.
    -   Action:
        1.  Parse response type (Info, Action Request, Confirmation Request).
        2.  Append assistant message to `session_state.messages`.
        3.  **If Confirmation Request**:
            -   Set `session_state.confirmation_pending = True`.
            -   Render Confirmation Prompt with visual emphasis.
        4.  **If Tool Response**:
            -   Render structured tool output (e.g., table for transactions).
        5.  **If Info**:
            -   Render text response.

3.  **Confirmation Event**
    -   Trigger: User types input while `confirmation_pending` is True.
    -   Action:
        1.  Call `orchestrator.handle_confirmation(text)`.
        2.  **If Confirmed ("YES")**:
            -   Show success message.
            -   Reset `confirmation_pending = False`.
        3.  **If Cancelled**:
            -   Show cancellation message.
            -   Reset `confirmation_pending = False`.

4.  **Debug Toggle Event**
    -   Trigger: User checks "Show Debug Info".
    -   Action: Re-render sidebar with debug JSON.
