"""Counterfactual branch specification and execution."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.action import AgentAction
from blindspot.counterfactuals.candidates import CounterfactualCandidate
from blindspot.interventions.base import InterventionApplication


class CounterfactualBranchSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    branch_id: str
    source_verified_id: str
    source_step: int
    source_snapshot_id: str
    candidate: CounterfactualCandidate
    intervention: InterventionApplication | None = None
    seed_policy: Literal["same_rng_state", "fixed_branch_seed", "resampled"] = "same_rng_state"
    max_steps: int = 10
    continuation_policy_id: str = "scripted"


class BranchComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_branch_id: str
    counterfactual_branch_id: str
    source_goal_score: float = 0.0
    counterfactual_goal_score: float = 0.0
    source_harm_score: float = 0.0
    counterfactual_harm_score: float = 0.0
    source_policy_violations: int = 0
    counterfactual_policy_violations: int = 0
    utility_retention: float = 0.0
    intervention_cost: float = 0.0
    prevented_harm: bool = False
    delayed_harm: bool = False
    recovery_improved: bool = False
    evidence_ids: list[str] = Field(default_factory=list)


class BranchResult(BaseModel):
    model_config = ConfigDict(frozen=False)

    branch_id: str
    source_verified_id: str
    source_step: int
    intervention_id: str
    status: str = "completed"
    goal_score: float = 0.0
    harm_score: float = 0.0
    policy_violations: int = 0
    steps: list[dict[str, Any]] = Field(default_factory=list)
    final_state: dict[str, Any] = Field(default_factory=dict)
    lineage: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
