"""Point-of-no-return estimation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PointOfNoReturnResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    estimated_step: int | None = None
    target_event: str = "realized_harm"
    branch_search_complete: bool = False
    preventable_before: list[int] = Field(default_factory=list)
    unpreventable_after: list[int] = Field(default_factory=list)
    uncertainty: float = 0.5
    evidence_branch_ids: list[str] = Field(default_factory=list)


def estimate_ponr(
    steps: list[dict[str, Any]],
    harm_steps: list[int],
    precursor_steps: list[int],
    target_event: str = "realized_harm",
) -> PointOfNoReturnResult:
    """
    Conservative PONR estimate using precursors and harm steps.

    Without full branch search, we use the last precursor step before the
    first harm as a conservative (early) PONR estimate.
    """
    if not harm_steps:
        return PointOfNoReturnResult(
            target_event=target_event, branch_search_complete=False,
            uncertainty=0.8,
        )

    first_harm = min(harm_steps)
    preventable: list[int] = []
    unpreventable: list[int] = []

    for step_dict in steps:
        s = step_dict.get("step", 0)
        if s < first_harm:
            preventable.append(s)
        elif s >= first_harm:
            unpreventable.append(s)

    # PONR = last precursor before harm (conservative)
    precursors_before_harm = [p for p in precursor_steps if p < first_harm]
    ponr_step = max(precursors_before_harm) if precursors_before_harm else first_harm - 1

    return PointOfNoReturnResult(
        estimated_step=ponr_step,
        target_event=target_event,
        branch_search_complete=False,  # Full search requires branch execution
        preventable_before=sorted(set(preventable)),
        unpreventable_after=sorted(set(unpreventable)),
        uncertainty=0.4,
    )
