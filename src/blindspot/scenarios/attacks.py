"""Attack binding specification for scenarios."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScenarioAttackBinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    attack_id: str
    instance_id: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    activation_condition: dict[str, Any] = Field(default_factory=dict)
    applies_to_sessions: list[str] = Field(default_factory=list)
    expected_progress_graph_id: str | None = None
    clean_control_id: str | None = None
