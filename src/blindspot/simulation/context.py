"""Simulation context and session state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationContext(BaseModel):
    model_config = ConfigDict(frozen=False)

    run_id: str
    episode_id: str
    scenario_id: str
    domain_id: str
    session_id: str
    step: int = 0
    global_step: int = 0
    seed: int = 42
    current_time: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    actor_id: str = "agent"
    remaining_steps: int = 20
    remaining_tool_calls: int = 10
    remaining_sessions: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)

    def advance(self) -> None:
        self.step += 1
        self.global_step += 1
        self.remaining_steps -= 1


class SessionState(BaseModel):
    model_config = ConfigDict(frozen=False)

    session_id: str
    session_index: int = 0
    started_at_step: int = 0
    ended_at_step: int | None = None
    active_actor_ids: list[str] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    persisted_memory_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})
