"""Dual-agent episode result."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DualAgentEpisodeResult(BaseModel):
    model_config = ConfigDict(frozen=False)

    run_id: str
    scenario_id: str
    attack_family: str
    seed: int
    status: str = "completed"  # completed | truncated | error
    total_turns: int = 0
    total_tool_calls: int = 0
    user_model: str = ""
    execution_model: str = ""
    judge_model: str = ""
    conversation_transcript: str = ""
    final_state_hash: str = ""
    tool_calls_summary: list[str] = Field(default_factory=list)
    run_dir: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
