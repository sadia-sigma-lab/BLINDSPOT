# Architecture

## Core vs Plugins

The `blindspot` package defines only abstract interfaces and registries. It never imports concrete domain, attack, or scenario implementations. All concrete components live in plugins (Python packages that implement `BenchmarkPlugin.register()`).

## Data Flow

```
ScenarioSpec (YAML)
    ↓
BenchmarkEngine.reset(scenario, seed)
    → Domain.initial_state() → WorldState
    → Domain.build_observation() → Observation
    ↓
Actor.act(Observation) → AgentAction
    ↓
BenchmarkEngine.step(action)
    → Tool.execute(state, ...) → ToolResult + StateDiff
    → apply_diff(state, diff) → WorldState'
    → EventQueue.due_events() → processed events
    → Domain.build_observation() → Observation'
    → TrajectoryStep recorded
    ↓
Evaluator.evaluate(initial, final, trajectory, scenario) → EvaluationResult
```

## State Transitions

Every mutating tool returns a `StateDiff` (list of `StateMutation` objects). The engine applies the diff to the current `WorldState` to produce the next state. The pre- and post-state SHA-256 hashes are stored in `TrajectoryStep`.

## Registries

All component types use `ComponentRegistry[T]`. The `RegistryHub` holds one registry per type (domains, tools, attacks, scenarios, evaluators, actors, policies, interventions).

## Runtime Engine

`BenchmarkEngine` is domain-agnostic. It delegates observation building and initial state construction to the registered `Domain`. It exposes `RuntimeHooks` for attacks, defenses, monitors, and interventions to attach without modifying the engine.

## Storage

All artifacts under `data/raw/runs/<run_id>/` are write-once. Replay reads the raw trajectory and applies it to a fresh engine instance.

## Replay

`replay_trajectory()` re-runs the recorded `AgentAction` sequence from the same initial state and seed. State hashes are compared step-by-step; the first mismatch is reported as divergence.

## Future: Attacks and RL

- **Attacks** inject into the engine via `RuntimeHooks` (e.g., `before_observation` to poison messages).
- **RL** wraps `BenchmarkEngine` in a Gymnasium-compatible `BenchmarkEnvironment` using the existing `step()` return signature `(obs, rewards, costs, terminated, truncated, info)`.
