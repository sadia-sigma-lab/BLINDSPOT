"""Utility retention scoring."""

from __future__ import annotations

from typing import Any


def compute_utility_retention(
    source_goal_score: float,
    branch_goal_score: float,
    source_subgoals: int = 0,
    branch_subgoals: int = 0,
    extra_steps: int = 0,
) -> float:
    """
    Normalized utility retention: how much of the original goal value is preserved.

    score = branch_goal / max(source_goal, epsilon)
    Capped at [0, 1]. Extra steps apply a small penalty.
    """
    epsilon = 1e-6
    base = branch_goal_score / max(source_goal_score, epsilon)
    step_penalty = min(0.3, extra_steps * 0.05)
    return max(0.0, min(1.0, base - step_penalty))
