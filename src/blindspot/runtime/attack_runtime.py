"""Attack runtime — initializes, dispatches, and tracks configured attacks."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from blindspot.attacks.base import Attack
from blindspot.attacks.budget import check_budget
from blindspot.attacks.config import AttackBudgetUsage, AttackConfig
from blindspot.attacks.context import AttackContext, build_attack_context
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.registry import AttackRegistry
from blindspot.attacks.state import AttackState
from blindspot.attacks.trace import AttackTraceStep, AttackTraceStore, _hash_context
from blindspot.core.scenario import ScenarioSpec
from blindspot.core.state import WorldState
from blindspot.core.trajectory import TrajectoryStep


class AttackRuntimeInstance:
    """Manages one active attack within a running episode."""

    def __init__(self, attack: Attack, config: AttackConfig) -> None:
        self.attack = attack
        self.config = config
        self.state: AttackState | None = None
        self.budget_usage = AttackBudgetUsage()
        self.initialized = False

    def initialize(self, scenario: ScenarioSpec, context: AttackContext) -> None:
        self.state = self.attack.initialize(self.config, scenario, context)
        self.initialized = True

    def dispatch(
        self,
        hook: AttackHook,
        context: AttackContext,
    ) -> tuple[AttackState, AttackEffect]:
        assert self.state is not None
        if self.state.is_terminal():
            return self.state, AttackEffect.noop()

        # Budget check
        if self.budget_usage.is_exhausted(self.config.budget):
            self.state.aborted = True
            self.state.abort_reason = "budget_exhausted"
            return self.state, AttackEffect.noop()

        new_state, effect = self.attack.on_hook(hook, self.state, context)
        if not effect.is_empty() and not effect.no_op:
            self.budget_usage.payloads += 1
            self.budget_usage.turns += 1

        self.state = new_state
        return self.state, effect


class AttackRuntime:
    """Coordinates all attacks for one episode."""

    def __init__(
        self,
        registry: AttackRegistry,
        scenario: ScenarioSpec,
        trace_dir: Path | None = None,
    ) -> None:
        self._registry = registry
        self._scenario = scenario
        self._instances: list[AttackRuntimeInstance] = []
        self._trace_store: AttackTraceStore | None = (
            AttackTraceStore(trace_dir) if trace_dir else None
        )
        self._message_history: list[dict[str, Any]] = []
        self._tool_call_history: list[dict[str, Any]] = []
        self._tool_result_history: list[dict[str, Any]] = []

    def initialize_attacks(
        self,
        attack_configs: list[AttackConfig],
        world_state: WorldState,
        run_id: str,
        episode_id: str,
        session_id: str,
        seed: int,
        current_time: datetime | None = None,
    ) -> None:
        now = current_time or datetime.now(tz=timezone.utc)
        for cfg in attack_configs:
            if not cfg.enabled:
                continue
            if not self._registry.contains(cfg.attack_id):
                continue
            attack = self._registry.get(cfg.attack_id)
            instance = AttackRuntimeInstance(attack, cfg)
            context = build_attack_context(
                world_state=world_state,
                knowledge_tier=cfg.knowledge_tier,
                run_id=run_id,
                episode_id=episode_id,
                scenario_id=self._scenario.scenario_id.canonical(),
                domain_id=self._scenario.domain_id.canonical(),
                step=0,
                session_id=session_id,
                seed=seed,
                current_time=now,
                target_actor_id=cfg.target_actor_id,
            )
            instance.initialize(self._scenario, context)
            self._instances.append(instance)

    def fire_hook(
        self,
        hook: AttackHook,
        world_state: WorldState,
        step: int,
        session_id: str,
        run_id: str,
        episode_id: str,
        seed: int,
        current_time: datetime | None = None,
    ) -> AttackEffect:
        """Fire hook across all active attacks; return composed effect."""
        if not self._instances:
            return AttackEffect.noop()

        now = current_time or datetime.now(tz=timezone.utc)
        effects: list[tuple[AttackEffect, int, str]] = []

        for instance in self._instances:
            if not instance.initialized or instance.state is None:
                continue

            context = build_attack_context(
                world_state=world_state,
                knowledge_tier=instance.config.knowledge_tier,
                run_id=run_id,
                episode_id=episode_id,
                scenario_id=self._scenario.scenario_id.canonical(),
                domain_id=self._scenario.domain_id.canonical(),
                step=step,
                session_id=session_id,
                seed=seed,
                current_time=now,
                target_actor_id=instance.config.target_actor_id,
                tool_call_history=self._tool_call_history,
                tool_result_history=self._tool_result_history,
                message_history=self._message_history,
            )

            state_before_snap = instance.state.model_dump()
            new_state, effect = instance.dispatch(hook, context)

            if self._trace_store and instance.state:
                trace_step = AttackTraceStep(
                    attack_instance_id=instance.state.attack_instance_id,
                    step=step,
                    session_id=session_id,
                    hook=hook,
                    visible_context_hash=_hash_context(context),
                    state_before=state_before_snap,
                    effect=effect.model_dump(),
                    state_after=new_state.model_dump(),
                    budget_usage=instance.budget_usage.model_copy(),
                )
                self._trace_store.append_step(
                    instance.attack.metadata.attack_id.canonical(), trace_step
                )

            if not effect.is_empty() and not effect.no_op:
                effects.append((effect, 0, instance.attack.metadata.attack_id.canonical()))

        if not effects:
            return AttackEffect.noop()

        from blindspot.attacks.insertion import compose_effects
        return compose_effects(effects, "merge_if_compatible")

    def record_tool_call(self, tool_call: dict[str, Any]) -> None:
        self._tool_call_history.append(tool_call)

    def record_tool_result(self, tool_result: dict[str, Any]) -> None:
        self._tool_result_history.append(tool_result)

    def record_message(self, message: dict[str, Any]) -> None:
        self._message_history.append(message)

    def evaluate_all_success(
        self,
        world_state: WorldState,
        trajectory: list[TrajectoryStep],
    ) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for instance in self._instances:
            if not instance.initialized or instance.state is None:
                continue
            aid = instance.attack.metadata.attack_id.canonical()
            progress = instance.attack.evaluate_progress(instance.state, world_state, trajectory)
            success = instance.attack.evaluate_success(instance.state, world_state, trajectory)
            results[aid] = {
                "success": success.model_dump(),
                "progress": progress.model_dump(),
                "budget_usage": instance.budget_usage.model_dump(),
            }
        return results
