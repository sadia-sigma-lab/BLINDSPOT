# Policy Model

## Dual Form

Policies exist in two forms:
1. **Structured** (`PolicyDocument` + `PolicyRule`) — machine-evaluatable
2. **Human-readable** (Markdown, linked via `human_readable_path`)

## Rule Effects

- `allow` — explicitly permits the action
- `deny` — blocks regardless of permissions (highest priority wins)
- `require_approval` — allowed only if a matching valid `ApprovalRecord` exists
- `require_verification` — external verification needed (placeholder for future skill)

## Priority

Higher `priority` values are evaluated first. A `deny` at priority 200 overrides an `allow` at priority 50.
