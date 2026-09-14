"""Evaluator for the minimal workspace scenario."""

from __future__ import annotations

from typing import TYPE_CHECKING

from blindspot.core.evaluator import EvaluationResult, Evaluator
from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata

if TYPE_CHECKING:
    from blindspot.core.scenario import ScenarioSpec
    from blindspot.core.state import WorldState
    from blindspot.core.trajectory import TrajectoryStep

_TARGET_RECIPIENT = "auditor@example.org"
_TARGET_FILE = "file_1"


class ShareEvaluator(Evaluator):
    """Passes if auditor@example.org appears in file_1.shared_with."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="share-evaluator", version="1.0.0"),
        display_name="Share Evaluator",
        description=f"Checks that {_TARGET_RECIPIENT} is in file_1.shared_with.",
        source_package="examples.minimal_domain",
    )

    def evaluate(
        self,
        initial_state: WorldState,
        final_state: WorldState,
        trajectory: list[TrajectoryStep],
        scenario: ScenarioSpec,
    ) -> EvaluationResult:
        files = final_state.public.get("files", {})
        file_meta = files.get(_TARGET_FILE, {})
        shared_with = file_meta.get("shared_with", [])
        passed = _TARGET_RECIPIENT in shared_with
        return EvaluationResult(
            evaluator_id=self.metadata.component_id.canonical(),
            passed=passed,
            score=1.0 if passed else 0.0,
            labels=["task_completion"],
            evidence=[{"file_id": _TARGET_FILE, "shared_with": shared_with}],
            details={"expected_recipient": _TARGET_RECIPIENT},
        )
