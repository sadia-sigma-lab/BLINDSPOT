# Clean Controls

Every adversarial scenario has a clean control counterpart that:

- removes or replaces adversarial payloads with benign content
- preserves benign task difficulty
- uses `core:benign-control@1.0.0` as the no-op baseline
- validates that attack success predicates are NOT satisfied at initialization

`CleanControlSpec` links a control to its source attack and declares the transformation type: `remove_payload`, `benign_payload`, `trusted_source`, `safe_target`, or `no_activation`.
