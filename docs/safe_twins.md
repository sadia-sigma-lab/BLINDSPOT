# Safe Counterfactual Twins

## Purpose

Every adversarial scenario should have a safe twin that:
- preserves benign task difficulty
- deactivates or removes the attack
- validates that attack success predicates are NOT satisfied at initialization

## Transformations

- `remove_payload` — removes all attack bindings
- `benign_payload` — disables all attacks
- `trusted_source` — replaces untrusted message source with trusted
- `safe_target` — replaces harmful target recipient with safe one
- `no_activation` — prevents attack from activating

## Usage

```python
twin_dict, twin_spec = generate_safe_twin(source_spec, "remove_payload")
```

`twin_spec.changed_fields` documents what was modified.
