# Verification Architecture

## Pipeline order (22 steps)

1. Validate run manifest
2. Validate artifact checksums
3. Validate trajectory schema and completeness
4. Replay trajectory — verify state-hash chain
5. Verify pre/post state hashes
6. Verify tool calls (registered, enabled, schema)
7. Verify authorization and approvals
8. Verify state diffs, audits, events
9. Evaluate benign and partial goals (deterministic)
10. Evaluate unsafe actions, precursors, harm (deterministic)
11. Evaluate policy compliance (deterministic)
12. Verify attack activation, progress, success (deterministic)
13. Evaluate recovery (deterministic)
14. Evaluate over-refusal (deterministic + flag for judges)
15. Assign diagnostic failure labels
16. Extract unresolved semantic questions
17. Run LLM judges (only for unresolved semantics)
18. Analyze judge disagreement
19. Adjudicate
20. Create correction proposals (never modifying raw data)
21. Calculate quality and confidence
22. Store verified artifacts

## Core rule

**Deterministic checks always run before judges.** A deterministic state predicate outranks any judge claim about the same objective fact.

## Hidden state guarantee

`verify_goals`, `verify_harms` and all other deterministic evaluators call `redact_hidden_labels()` before building evidence. Judge prompts receive only redacted evidence.
