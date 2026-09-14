# Prompt System

## Ordering

1. System instructions (template version, actor role, domain)
2. Benign user objective
3. Visible domain policies
4. Discoverable tool schemas (filtered by scenario tool binding)
5. Visible memory records
6. Conversation history
7. Current observation (messages + tool results)

## Isolation guarantees

- `redact_hidden_labels()` strips `grading_target`, `attack_ground_truth`, `__*` keys
- `redact_secrets()` strips configurable regex patterns with `[REDACTED]`
- Tool schemas are filtered to enabled + visible tools only
- Actor-specific visibility profile controls what state appears

## Provenance

`PromptArtifact.source_hashes` contains SHA-256 hashes of messages, tools, and template IDs.
`PromptArtifact.template_ids` lists all templates used (versioned).
