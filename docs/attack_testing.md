# Testing Attacks

## Unit pattern

```python
def test_my_attack_adds_message():
    attack = MyAttack()
    cfg = AttackConfig(attack_id="...", seed=42, target_actor_id="agent", budget=AttackBudget(max_payloads=3))
    ctx = build_attack_context(world_state=state, knowledge_tier=..., ...)
    state = attack.initialize(cfg, scenario, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_OBSERVATION, state, ctx)
    assert len(effect.messages_to_add) == 1
```

## Determinism check

```python
assert _run(seed=42) == _run(seed=42)  # same effect
```

## Hidden state check

```python
assert "grading" not in str(ctx.visible_state)
assert "attack_state" not in str(ctx.visible_state)
```
