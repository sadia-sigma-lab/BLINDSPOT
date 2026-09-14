# Scenario Cards

Each scenario generates a YAML card summarizing:
- scenario_id, title, domain
- benign_goal
- attack_family, hazard_family
- horizon (max_steps, dependency_span, sessions)
- critical_decisions
- safe_twin
- evaluator_types
- intended_tracks

```bash
blindspot scenario card --scenario workspace:clean-external-sharing-001@1.0.0
```
