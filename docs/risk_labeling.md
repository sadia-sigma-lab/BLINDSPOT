# Multi-Horizon Risk Labeling

## Label definitions

For event type `e` and horizon `K` at step `t`:

```
z[t,e,K] = first_event_step  if event occurs in (t, t+K]
z[t,e,K] = 0                 if horizon fully observed and no event
z[t,e,K] = None              if trajectory ends before t+K and no event (CENSORED)
```

**Censored horizons are stored as `None` — never mapped to 0.**

## Event targets

- `unsafe_action` — tool call that violates a policy
- `realized_harm` — unauthorized sharing of restricted/confidential data  
- `policy_violation` — explicit policy rule broken
- `attack_success` — attack success predicate satisfied

## Precursor detection

A step is an unsafe precursor when it:
- reads a sensitive resource before it is later shared inappropriately
- directly expands privilege (e.g., sharing a confidential/restricted file)

Precursors are evidence-backed and conservative: benign actions are not labeled.

## Time-to-event

`T[t,e]` = minimum steps from `t` to first future event `e`. Returns `None` when no event occurs.

## Usage for training

```python
from blindspot.risk.generators import RiskLabelGenerator
from blindspot.risk.config import RiskLabelConfig

gen = RiskLabelGenerator(RiskLabelConfig(config_id="default"))
step_labels, ponr, recov = gen.generate(verified_id, raw_run_id, run_dir)
```
