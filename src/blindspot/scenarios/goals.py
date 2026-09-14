"""Benign task specification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BenignTaskSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: str
    instruction: str
    user_actor_id: str
    target_actor_id: str
    goal_predicates: list[str]
    required_information: list[str] = Field(default_factory=list)
    expected_subgoals: list[str] = Field(default_factory=list)
    allowed_variants: list[str] = Field(default_factory=list)
    optional_goals: list[str] = Field(default_factory=list)
    communication_requirements: list[str] = Field(default_factory=list)
