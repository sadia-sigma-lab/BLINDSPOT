# Preference Pairs and Training Exports

## Preference types

- `safe_over_unsafe` — intervention prevents harm with utility ≥ 0.5 and margin ≥ 0.1
- `higher_utility_safe` — same safety level, CF achieves higher goal score
- `recovery_over_no_recovery` — CF achieves better recovery

## Rules

- Pairs require margin ≥ 0.1 on the target dimension
- Quarantined branches cannot generate training pairs
- Unverified branches are excluded by default

## Export formats

| Format | Use |
|--------|-----|
| `risk_prediction` | Step + multi-horizon label training |
| `process_supervision` | Per-step safe/unsafe process reward |
| `offline_rl` | (obs, action, cost, next_obs, terminated, truncated) transitions |
| `preference` | Preference pairs for DPO / RLHF |

```bash
blindspot risk export --risk-labeled-id <id> --format risk_prediction
blindspot risk export --risk-labeled-id <id> --format offline_rl
```

Note: `reward` field in offline RL transitions is a placeholder until Skill 09 assigns final values.
