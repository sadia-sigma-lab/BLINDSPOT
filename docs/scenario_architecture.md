# Scenario Architecture

## Core principle

Scenarios are declarative specifications — no runtime logic embedded in YAML. The same schema is used for hand-authored, generated, and mutated scenarios.

## `FullScenarioSpec` structure

- `metadata` — stable ID, version, source, tracks
- `initial_state` — fixture ID, seed, overrides
- `actors` — unique actor list with types and roles
- `task` — benign user objective with goal predicates
- `policies` — policy bindings and enforcement rules
- `tools` — enabled/disabled tool set per domain
- `attacks` — attack bindings with config and clean control links
- `hazards` — non-adversarial risks
- `events` — scheduled environment events
- `horizon` — multi-axis episode constraints
- `decision_points` — critical moments for intervention/supervision
- `safe_alternatives` — known safe execution paths
- `outcomes` — predicates for success/failure/unsafe/refusal
- `recovery` — post-harm recovery specification
- `difficulty` — transparent multi-axis scoring
- `splits` — dataset split and leakage metadata
- `hidden` — verifier-only grading state (never projected to agent)

## Validation flow

`validate_scenario()` → checks actors, tools, attacks, horizon, hidden isolation → returns `ScenarioValidationReport`

Only validated scenarios enter `ScenarioRegistry`.
