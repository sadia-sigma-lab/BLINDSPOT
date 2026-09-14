"""Scenario event schedule specification."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ScenarioEventSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    event_type: str
    trigger: dict[str, Any]
    payload: dict[str, Any] = Field(default_factory=dict)
    visibility: Literal["public", "private", "hidden"] = "private"
    actor_id: str | None = None
    repeat: dict[str, Any] | None = None
    cancellation_conditions: list[str] = Field(default_factory=list)
