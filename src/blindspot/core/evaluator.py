"""Evaluator abstract interface and result contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.metadata import ComponentMetadata

if TYPE_CHECKING:
    from blindspot.core.scenario import ScenarioSpec
    from blindspot.core.state import WorldState
    from blindspot.core.trajectory import TrajectoryStep


class EvaluationResult(BaseModel):
    """Result produced by an evaluator after inspecting a completed episode."""

    model_config = ConfigDict(frozen=True)

    evaluator_id: str
    passed: bool
    score: float | None = None
    labels: list[str] = []
    evidence: list[dict[str, Any]] = []
    details: dict[str, Any] = {}


class Evaluator(ABC):
    """Abstract interface for post-episode evaluation."""

    metadata: ComponentMetadata

    @abstractmethod
    def evaluate(
        self,
        initial_state: WorldState,
        final_state: WorldState,
        trajectory: list[TrajectoryStep],
        scenario: ScenarioSpec,
    ) -> EvaluationResult:
        """Evaluate the episode and return a structured result."""
        ...
