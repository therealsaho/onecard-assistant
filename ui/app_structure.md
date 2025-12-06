# App Structure

## UI Components

### 1. Chat Window
- **Layout**: Central column, scrollable container.
- **Message Bubbles**:
    - **User**: Right-aligned, distinct color.
    - **Assistant**: Left-aligned, neutral color.
    - **System/Audit**: Centered, small gray text (for audit logs).

### 2. User Input Area
- **Text Input**: Fixed at the bottom.
- **Send Button**: Standard submit action.
- **Voice Input Placeholder**:
    - Visual indicator (microphone icon).
    - Status text: "Listening..." (when active).

### 3. Assistant Streaming Placeholder
- Reserved area for streaming tokens during generation.
- Visual cursor or typing indicator.

### 4. Developer Debug Panel
- **Toggle**: Checkbox in sidebar "Show Debug Info".
- **Content**:
    - Router Classification (Intent, Confidence).
    - Tool Name & Arguments.
    - Raw Model Output.
    - Latency metrics.

## State Handling

### Session State Keys
- `messages`: List of message objects `[{role, content, type}]`.
- `user_id`: Authenticated user ID (mocked as "12345").
- `confirmation_pending`: Boolean, true if waiting for "YES".
- `pending_action`: Object storing the action payload waiting for confirmation.

### Reset Rules
- **Hard Reset**: "Clear Chat" button in sidebar clears `messages` (except system init).
- **Soft Reset**: After a confirmed action is completed, `confirmation_pending` is reset to false.
