# Attack Architecture

## Core principle

Attack logic never lives in the core runtime. Attacks are plugins that bind to lifecycle hooks.

## Components

- **AttackRegistry**: ordered map of `attack_id → Attack`
- **AttackRuntime**: manages active instances, fires hooks, composes effects, persists traces
- **AttackContext**: knowledge-tier-filtered view of world state passed to each attack
- **AttackEffect**: all modifications an attack may produce at one hook point
- **AttackState**: verifier-visible tracking state (not exposed to agent)

## Lifecycle

1. `AttackRuntime.initialize_attacks()` — instantiate attacks with configs
2. For each lifecycle event, `fire_hook(hook, world_state, ...)` dispatches to all active attacks
3. Effects are composed (parallel merge or sequential stop-first)
4. Effects applied through runtime adapters — never direct state mutation
5. Budget usage incremented; trace step appended
6. Success/abort predicates evaluated at episode end

## Hidden state guarantee

`AttackState.verifier_only` and hidden world state are never included in `AttackContext.visible_state`.
