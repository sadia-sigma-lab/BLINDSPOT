"""Agent request and response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    episode_id: str
    session_id: str
    step: int
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]]
    response_format: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    response_id: str
    raw_content: Any
    text: str | None = None
    native_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = None
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, Any] | None = None
