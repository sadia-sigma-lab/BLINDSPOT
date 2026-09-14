"""Abstract attack interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from blindspot.attacks.config import AttackBudget, AttackBudgetUsage, AttackConfig
from blindspot.attacks.context import AttackContext
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.metadata import AttackMetadata
from blindspot.attacks.predicates import AttackPredicateResult
from blindspot.attacks.progress import AttackProgressResult
from blindspot.attacks.state import AttackState

if TYPE_CHECKING:
    from blindspot.core.scenario import ScenarioSpec
    from blindspot.core.state import WorldState
    from blindspot.core.trajectory import TrajectoryStep
    from blindspot.attacks.payload import ScheduledPayload


class Attack(ABC):
    """Abstract base for all benchmark attacks."""

    metadata: AttackMetadata

    @property
    def config_model(self) -> type[AttackConfig]:
        return AttackConfig

    @abstractmethod
    def initialize(
        self,
        config: AttackConfig,
        scenario: "ScenarioSpec",
        context: AttackContext,
    ) -> AttackState:
        """Initialize attack state; return the starting AttackState."""
        ...

    @abstractmethod
    def on_hook(
        self,
        hook: AttackHook,
        state: AttackState,
        context: AttackContext,
    ) -> tuple[AttackState, AttackEffect]:
        """React to a lifecycle hook; return updated state and effect."""
        ...

    @abstractmethod
    def evaluate_progress(
        self,
        state: AttackState,
        world_state: "WorldState",
        trajectory: list["TrajectoryStep"],
    ) -> AttackProgressResult:
        ...

    @abstractmethod
    def evaluate_success(
        self,
        state: AttackState,
        world_state: "WorldState",
        trajectory: list["TrajectoryStep"],
    ) -> AttackPredicateResult:
        ...

    def should_activate(self, hook: AttackHook, state: AttackState, context: AttackContext) -> bool:
        """Return True if this attack should fire at the given hook."""
        if state.is_terminal():
            return False
        return hook.value in self.metadata.required_hooks


class StaticAttack(Attack):
    """Attack that delivers pre-determined payloads based on config and seed."""

    @abstractmethod
    def payload_schedule(self, state: AttackState) -> list["ScheduledPayload"]:
        """Return the full ordered payload delivery schedule."""
        ...


class AdaptiveAttack(Attack):
    """Attack that adapts its behavior based on observed agent responses."""

    @abstractmethod
    def observe(
        self,
        state: AttackState,
        context: AttackContext,
    ) -> AttackState:
        """Update attacker memory based on latest context."""
        ...

    @abstractmethod
    def propose_next_effect(
        self,
        state: AttackState,
        context: AttackContext,
    ) -> AttackEffect:
        """Generate the next adversarial effect given current observations."""
        ...

    def on_hook(
        self,
        hook: AttackHook,
        state: AttackState,
        context: AttackContext,
    ) -> tuple[AttackState, AttackEffect]:
        if not self.should_activate(hook, state, context):
            return state, AttackEffect.noop()
        updated_state = self.observe(state, context)
        updated_state.optimization_steps += 1
        effect = self.propose_next_effect(updated_state, context)
        return updated_state, effect
