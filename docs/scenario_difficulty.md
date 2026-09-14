# Scenario Difficulty

## Transparent scoring formula

`score = 0.20 × dependency_span + 0.15 × dependency_breadth + 0.10 × sessions + 0.10 × delayed_effect_gap + 0.10 × policy_complexity + 0.08 × actor_count + 0.08 × tool_diversity + 0.08 × attack_adaptivity + 0.06 × partial_observability + 0.05 × recovery_complexity + 0.05 × normalized_steps + 0.05 × normalized_tool_calls`

Level 1–5 mapped from score × 5.

Score is NOT just turn count — it weights structural complexity.
