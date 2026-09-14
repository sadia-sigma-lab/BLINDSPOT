"""Parse result contract."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.action import AgentAction


class ParseResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    action: AgentAction | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
    repair_attempted: bool = False
    repair_output: Any = None
    parser_id: str = "unknown"
