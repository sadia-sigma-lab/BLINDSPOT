"""Critical decision points and safe alternatives."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CriticalDecisionPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision_id: str
    description: str
    activation_predicate: str
    candidate_action_classes: list[str]
    preferred_safe_actions: list[str]
    unsafe_actions: list[str]
    point_of_no_return: bool = False
    expected_information_needed: list[str] = Field(default_factory=list)


class SafeAlternative(BaseModel):
    model_config = ConfigDict(frozen=True)

    alternative_id: str
    decision_id: str | None = None
    action_sequence: list[dict[str, Any]]
    preserves_utility: float = 1.0
    requires_approval: bool = False
    requires_clarification: bool = False
    expected_outcome_predicates: list[str] = Field(default_factory=list)
