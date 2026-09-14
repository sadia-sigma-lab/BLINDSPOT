"""Scenario outcome specification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OutcomeSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    benign_success_predicates: list[str]
    partial_success_predicates: list[str] = Field(default_factory=list)
    unsafe_outcome_predicates: list[str] = Field(default_factory=list)
    forbidden_action_predicates: list[str] = Field(default_factory=list)
    policy_violation_predicates: list[str] = Field(default_factory=list)
    over_refusal_predicates: list[str] = Field(default_factory=list)
    terminal_success_predicates: list[str] = Field(default_factory=list)
    terminal_failure_predicates: list[str] = Field(default_factory=list)
