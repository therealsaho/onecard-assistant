# LLM Router

The `LLMRouter` is responsible for classifying user intents into actionable categories. It supports two modes:

1.  **Mock Mode (Default)**: Uses keyword-based heuristics for offline/deterministic behavior.
2.  **Real Mode**: Uses an LLM (Gemini/OpenAI) to classify intent with higher flexibility.

## Configuration

To enable Real Mode, set the environment variable:
```bash
USE_REAL_LLM_ROUTER=true
```

## Schema

The router returns a dictionary with the following structure:
```json
{
  "intent": "action" | "info" | "ambiguous",
  "action_type": "string" | null,
  "confidence": float (0.0 - 1.0)
}
```

## Supported Intents

- **action**: Destructive or state-changing actions (e.g., block card).
- **info**: Read-only information retrieval (e.g., get balance).
- **ambiguous**: Unclear or unsupported requests.
