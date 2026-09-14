"""Agent configuration contract."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    agent_id: str
    adapter_id: str
    model_name: str
    provider: str
    temperature: float = 0.0
    top_p: float | None = None
    max_output_tokens: int | None = None
    reasoning_effort: str | None = None
    timeout_seconds: float = 120.0
    max_retries: int = 2
    deterministic: bool = False
    supports_native_tools: bool = True
    supports_json_mode: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)
