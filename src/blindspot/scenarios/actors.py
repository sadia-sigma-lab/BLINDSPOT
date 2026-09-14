"""Scenario actor specifications."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScenarioActorSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor_id: str
    actor_type: Literal[
        "target_agent", "user", "attacker", "background_actor",
        "monitor", "approver", "collaborator",
    ]
    role_id: str | None = None
    organization_id: str | None = None
    simulator_id: str | None = None
    tool_access_profile: str | None = None
    visibility_profile: str = "default"
    objective_ids: list[str] = Field(default_factory=list)
    behavior_parameters: dict[str, Any] = Field(default_factory=dict)
