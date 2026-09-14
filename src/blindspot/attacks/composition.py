"""Attack composition — sequential, parallel, conditional, nested."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.base import Attack
from blindspot.attacks.config import AttackConfig
from blindspot.attacks.context import AttackContext
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.insertion import compose_effects
from blindspot.attacks.predicates import AttackPredicateResult
from blindspot.attacks.progress import AttackProgressResult
from blindspot.attacks.state import AttackState


class AttackCompositionSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    composition_id: str
    attack_ids: list[str]
    mode: Literal["sequential", "parallel", "conditional", "nested"]
    priorities: dict[str, int] = Field(default_factory=dict)
    conflict_policy: Literal["error", "highest_priority", "merge_if_compatible"] = "error"
    activation_conditions: dict[str, Any] = Field(default_factory=dict)


class ComposedAttack:
    """Runs multiple attacks together with a shared lifecycle."""

    def __init__(
        self,
        spec: AttackCompositionSpec,
        attacks: list[Attack],
    ) -> None:
        self.spec = spec
        self._attacks = attacks
        # Map attack_id → attack for deterministic iteration
        self._by_id: dict[str, Attack] = {
            a.metadata.attack_id.canonical(): a for a in attacks
        }

    def initialize_all(
        self,
        configs: dict[str, AttackConfig],
        scenario: Any,
        context: AttackContext,
    ) -> dict[str, AttackState]:
        states: dict[str, AttackState] = {}
        for attack in self._attacks:
            aid = attack.metadata.attack_id.canonical()
            cfg = configs.get(aid, AttackConfig(attack_id=aid, target_actor_id=context.target_actor_id, seed=context.seed))
            states[aid] = attack.initialize(cfg, scenario, context)
        return states

    def on_hook(
        self,
        hook: AttackHook,
        states: dict[str, AttackState],
        context: AttackContext,
    ) -> tuple[dict[str, AttackState], AttackEffect]:
        effects_with_priority: list[tuple[AttackEffect, int, str]] = []
        updated_states = dict(states)

        if self.spec.mode == "sequential":
            # Fire attacks in declared order; stop after first non-no-op
            for attack in self._attacks:
                aid = attack.metadata.attack_id.canonical()
                state = updated_states.get(aid)
                if state is None or state.is_terminal():
                    continue
                new_state, effect = attack.on_hook(hook, state, context)
                updated_states[aid] = new_state
                if not effect.is_empty() and not effect.no_op:
                    return updated_states, effect
            return updated_states, AttackEffect.noop()

        elif self.spec.mode == "parallel":
            for attack in self._attacks:
                aid = attack.metadata.attack_id.canonical()
                state = updated_states.get(aid)
                if state is None or state.is_terminal():
                    continue
                new_state, effect = attack.on_hook(hook, state, context)
                updated_states[aid] = new_state
                priority = self.spec.priorities.get(aid, 0)
                effects_with_priority.append((effect, priority, aid))

            composed = compose_effects(effects_with_priority, self.spec.conflict_policy)
            return updated_states, composed

        else:
            # conditional / nested: simplify to sequential for now
            return self.on_hook.__wrapped__(self, hook, states, context) if hasattr(self.on_hook, "__wrapped__") else (updated_states, AttackEffect.noop())
