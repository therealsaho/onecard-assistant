# Streamlit Contract

## Message Handling
- **Append Behavior**: New messages are appended to `st.session_state.messages`.
- **Rendering**: Iterate through `st.session_state.messages` and render using `st.chat_message`.

## Orchestrator Interface
The UI will call the following (mock) functions from the Orchestrator module:
- `orchestrator.process_user_input(text, user_id)` -> returns `response_object`
- `orchestrator.handle_confirmation(user_input, pending_action)` -> returns `response_object`

## UX Microcopy & Indicators
- **Processing**: Show `st.spinner("OneCard Assistant is thinking...")` while waiting for Orchestrator.
- **Awaiting Confirmation**:
    - Display a warning alert: "⚠️ Action requires confirmation. Type YES to proceed."
- **Success**:
    - Display success toast or green alert: "✅ Action Completed."

## Destructive Action Interface
- When `confirmation_pending` is true:
    - Render the last assistant message (the confirmation prompt) with a **RED** border or background highlight.
    - Disable other inputs if possible, or strictly route next input to confirmation handler.

## Error Boundary
- **LLM Failure**: Display "I'm having trouble connecting. Please try again." (Red banner).
- **Missing Tool Output**: Display "Tool execution failed. Please contact support."
- **RAG Miss**: Fallback to "I couldn't find that in the policy documents."
