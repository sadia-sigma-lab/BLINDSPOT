"""Preference pair generation from verified branch comparisons."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.counterfactuals.branching import BranchComparison, BranchResult

_MIN_MARGIN = 0.1  # minimum difference to generate a pair


class PreferencePair(BaseModel):
    model_config = ConfigDict(frozen=True)

    pair_id: str
    context_step: int
    source_verified_id: str
    preferred_branch_id: str
    dispreferred_branch_id: str
    preference_type: Literal[
        "safe_over_unsafe",
        "lower_cost_safe",
        "higher_utility_safe",
        "recovery_over_no_recovery",
        "verification_over_blind_action",
    ]
    margin: float
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.9
    metadata: dict[str, Any] = Field(default_factory=dict)


def generate_preference_pairs(
    source: BranchResult,
    counterfactual: BranchResult,
    comparison: BranchComparison,
    source_verified_id: str,
    source_step: int,
) -> list[PreferencePair]:
    """
    Generate preference pairs from a branch comparison.

    Pairs require verified outcome differences with meaningful margin.
    No pairs generated from quarantined branches.
    """
    pairs: list[PreferencePair] = []

    harm_margin = abs(comparison.source_harm_score - comparison.counterfactual_harm_score)
    goal_margin = abs(comparison.source_goal_score - comparison.counterfactual_goal_score)

    # Safe over unsafe: counterfactual prevents harm with acceptable utility
    if comparison.prevented_harm and harm_margin >= _MIN_MARGIN:
        if comparison.utility_retention >= 0.5:
            pairs.append(PreferencePair(
                pair_id=str(uuid.uuid4()),
                context_step=source_step,
                source_verified_id=source_verified_id,
                preferred_branch_id=counterfactual.branch_id,
                dispreferred_branch_id=source.branch_id,
                preference_type="safe_over_unsafe",
                margin=harm_margin,
                confidence=0.9,
            ))

    # Higher utility safe: same safety, counterfactual has higher goal score
    if (not comparison.prevented_harm
            and comparison.counterfactual_goal_score > comparison.source_goal_score
            and goal_margin >= _MIN_MARGIN
            and comparison.counterfactual_harm_score <= comparison.source_harm_score):
        pairs.append(PreferencePair(
            pair_id=str(uuid.uuid4()),
            context_step=source_step,
            source_verified_id=source_verified_id,
            preferred_branch_id=counterfactual.branch_id,
            dispreferred_branch_id=source.branch_id,
            preference_type="higher_utility_safe",
            margin=goal_margin,
            confidence=0.75,
        ))

    # Recovery improved
    if comparison.recovery_improved and goal_margin >= _MIN_MARGIN:
        pairs.append(PreferencePair(
            pair_id=str(uuid.uuid4()),
            context_step=source_step,
            source_verified_id=source_verified_id,
            preferred_branch_id=counterfactual.branch_id,
            dispreferred_branch_id=source.branch_id,
            preference_type="recovery_over_no_recovery",
            margin=goal_margin,
            confidence=0.8,
        ))

    return pairs
