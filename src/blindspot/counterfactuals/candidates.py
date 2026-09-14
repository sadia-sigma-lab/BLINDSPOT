"""Counterfactual candidate selection."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.action import AgentAction


class CounterfactualCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_id: str
    source_step: int
    actor_id: str
    action: AgentAction
    source: Literal[
        "scenario_safe_alternative",
        "intervention_catalog",
        "scripted_policy",
        "model_proposal",
    ]
    expected_effect: str
    requires_verification: bool = True
    oracle_only: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


def select_critical_steps(
    steps: list[dict[str, Any]],
    scenario: Any | None,
    harm_steps: list[int],
    precursor_steps: list[int],
    ponr_step: int | None,
    max_branches: int = 8,
) -> list[int]:
    """
    Select candidate branch points in priority order:
    1. Scenario critical decision points
    2. Unsafe precursor steps
    3. First harmful tool call
    4. Last step before PONR
    5. Recovery opportunities

    Returns sorted list of up to max_branches unique steps.
    """
    candidates: list[int] = []

    # 1. Scenario decision points
    if scenario is not None:
        for dp in getattr(scenario, "decision_points", []):
            candidates.append(dp.decision_id)  # just for reference

    # 2. Unsafe precursors
    candidates.extend(precursor_steps)

    # 3. First harm step
    if harm_steps:
        candidates.append(min(harm_steps))

    # 4. Step before PONR
    if ponr_step is not None and ponr_step > 0:
        candidates.append(ponr_step - 1)

    # 5. First tool call step
    for step_dict in steps:
        if (step_dict.get("selected_action") or {}).get("action_type") == "tool_call":
            candidates.append(step_dict.get("step", 0))
            break

    # Deduplicate, sort, cap
    unique = sorted(set(s for s in candidates if isinstance(s, int)))
    return unique[:max_branches]
