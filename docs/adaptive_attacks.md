# Adaptive Attacks

Adaptive attacks (subclass `AdaptiveAttack`) observe agent responses and update their strategy each step.

## Interface

```python
def observe(self, state, context) -> AttackState:
    # Update attacker_memory based on context.visible_tool_calls etc.
    ...

def propose_next_effect(self, state, context) -> AttackEffect:
    # Generate next adversarial message/modification
    ...
```

## Constraints

- Must obey `AttackBudget.max_optimization_steps`
- Only access information permitted by `knowledge_tier`
- Must be deterministic under fixed seed (use `random.Random(config.seed)`)
- Future: LLM-backed planners plug in via `AttackPlanner` adapter
