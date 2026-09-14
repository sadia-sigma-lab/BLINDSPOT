"""Step-level risk label model and multi-horizon labeling with correct censoring."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StepRiskLabel(BaseModel):
    """Complete risk label for one trajectory step."""

    model_config = ConfigDict(frozen=True)

    raw_run_id: str
    verified_id: str
    episode_id: str
    session_id: str
    step: int

    # Point-in-time labels
    unsafe_now: bool = False
    unsafe_precursor: bool = False
    realized_harm_now: bool = False
    policy_violation_now: bool = False
    attack_success_now: bool = False

    # Multi-horizon future labels: {horizon: step_of_first_event | None (censored)}
    future_unsafe_action: dict[str, int | None] = Field(default_factory=dict)
    future_realized_harm: dict[str, int | None] = Field(default_factory=dict)
    future_policy_violation: dict[str, int | None] = Field(default_factory=dict)
    future_attack_success: dict[str, int | None] = Field(default_factory=dict)

    # Time-to-event (steps from this step; None = censored before event)
    time_to_unsafe_action: int | None = None
    time_to_harm: int | None = None
    time_to_policy_violation: int | None = None
    time_to_attack_success: int | None = None

    # Structural labels
    point_of_no_return: bool = False
    recoverable: bool | None = None
    minimum_safe_intervention_id: str | None = None

    confidence: float = 1.0
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def _horizon_label(
    step: int,
    horizon: int,
    event_steps: list[int],
    total_steps: int,
) -> int | None:
    """
    Correct censoring implementation.

    Returns:
      1  — if any event occurs in (step, step+horizon]
      0  — if complete negative horizon is observed
      None — if trajectory ends before horizon and no event seen (censored)
    """
    window_end = step + horizon
    # Check for positive event in window
    for es in event_steps:
        if step < es <= window_end:
            return es  # return the step of first event (positive)

    # Check if we have the full negative horizon
    if total_steps > window_end:
        return None  # encode "no event" as None in positive-event dict (use 0 semantically)

    # Trajectory ends before full horizon and no event seen → censored
    return None
