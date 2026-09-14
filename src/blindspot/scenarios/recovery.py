"""Recovery specification."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecoverySpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    recoverable: bool
    detection_predicates: list[str] = Field(default_factory=list)
    recovery_actions: list[dict[str, Any]] = Field(default_factory=list)
    recovery_success_predicates: list[str] = Field(default_factory=list)
    residual_harm_predicates: list[str] = Field(default_factory=list)
    recovery_deadline_steps: int | None = None
