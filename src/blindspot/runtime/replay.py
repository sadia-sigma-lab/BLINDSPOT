"""Deterministic replay support."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.action import AgentAction
from blindspot.core.scenario import ScenarioSpec
from blindspot.core.trajectory import TrajectoryStep
from blindspot.registry import RegistryHub
from blindspot.runtime.engine import BenchmarkEngine


class ReplayReport(BaseModel):
    """Result of a deterministic replay verification."""

    model_config = ConfigDict(frozen=True)

    success: bool
    first_divergent_step: int | None = None
    expected_hash: str | None = None
    actual_hash: str | None = None
    details: dict[str, Any] = {}


def replay_trajectory(
    scenario: ScenarioSpec,
    seed: int,
    original_steps: list[TrajectoryStep],
    registries: RegistryHub,
) -> ReplayReport:
    """Re-run the recorded actions and compare state hashes step by step."""
    engine = BenchmarkEngine(registries)
    engine.reset(scenario, seed)

    for step in original_steps:
        action = step.parsed_action
        obs, rewards, costs, terminated, truncated, info = engine.step(action)

        session = engine.get_session()
        if session is None:
            break

        actual_hash = session.current_state_hash
        expected_hash = step.post_state_hash

        if actual_hash != expected_hash:
            return ReplayReport(
                success=False,
                first_divergent_step=step.step,
                expected_hash=expected_hash,
                actual_hash=actual_hash,
                details={"action": action.model_dump()},
            )

        if terminated or truncated:
            break

    return ReplayReport(success=True)
