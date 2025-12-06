# Acceptance Checklist

- [ ] **System Prompt**: Exists in `orchestrator/system_prompts.md` and is copy-paste ready.
- [ ] **Router Prompt**: Includes classification rules for `info`, `action`, and `ambiguous`.
- [ ] **Confirmation Template**: Exists and explicitly enforces "YES" token for destructive actions.
- [ ] **Tool Contracts**: Documented in `orchestrator/tool_descriptions.md` with exact JSON output samples.
- [ ] **Test Cases**: `orchestrator/test_cases.md` includes expected outputs for happy and failure paths.
- [ ] **Audit Schema**: One-line audit event schema is defined in `orchestrator/tool_descriptions.md`.
