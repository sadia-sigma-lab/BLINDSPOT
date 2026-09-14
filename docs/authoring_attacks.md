# Authoring Attacks

## Minimal attack

```python
class MyAttack(StaticAttack):
    metadata = AttackMetadata(
        attack_id=ComponentID(namespace="community", name="my-attack", version="1.0.0"),
        family="my_family", source=AttackSource.ENVIRONMENT,
        targets=[AttackTarget.INTENT], mechanisms=["indirect_injection"],
        temporal_patterns=[AttackTemporalPattern.ONE_SHOT],
        harm_categories=["confidentiality"],
        knowledge_tier=AttackerKnowledgeTier.TOOL_CALLS,
        required_hooks=["after_observation"],
    )

    def initialize(self, config, scenario, context) -> AttackState: ...
    def payload_schedule(self, state) -> list[ScheduledPayload]: ...
    def on_hook(self, hook, state, context) -> tuple[AttackState, AttackEffect]: ...
    def evaluate_progress(self, state, world_state, trajectory) -> AttackProgressResult: ...
    def evaluate_success(self, state, world_state, trajectory) -> AttackPredicateResult: ...
```

## Rules

- Never mutate world state directly — only return `AttackEffect`
- Only access state within declared knowledge tier
- Success must be determined by programmatic predicates, not attacker self-report
- Always provide a clean control counterpart
