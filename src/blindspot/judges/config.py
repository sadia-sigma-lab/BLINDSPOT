"""Judge configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class JudgeConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    judge_id: str
    adapter_id: str
    model_name: str
    provider: str
    temperature: float = 0.0
    max_output_tokens: int = 1200
    timeout_seconds: float = 120.0
    max_retries: int = 2
    supported_question_types: list[str] = Field(default_factory=list)
    deterministic: bool = False
