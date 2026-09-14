# Attack Composition

Multiple attacks run simultaneously via `ComposedAttack`.

## Modes

- `sequential` — fire in order; stop after first non-no-op effect
- `parallel` — all fire; effects merged via `conflict_policy`
- `conditional` / `nested` — simplified to sequential in current implementation

## Conflict policies

- `error` — raise on conflicting replace operations
- `highest_priority` — highest-priority attack wins
- `merge_if_compatible` — append all effects

## Per-attack state

Each attack in a composition maintains its own `AttackState` and budget counters.
