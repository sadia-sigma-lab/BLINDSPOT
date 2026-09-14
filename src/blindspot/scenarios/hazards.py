"""Hazard specification — non-adversarial risks."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HazardSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    hazard_id: str
    hazard_type: Literal[
        "ambiguous_instruction", "stale_state", "conflicting_policy",
        "duplicate_identity", "race_condition", "tool_failure",
        "expired_approval", "partial_observability", "delayed_effect",
        "resource_constraint",
    ]
    activation: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    expected_safe_behavior: list[str] = Field(default_factory=list)
