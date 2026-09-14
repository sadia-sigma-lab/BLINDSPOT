"""Tool execution result contract."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.state_diff import StateDiff
from blindspot.tools.errors import ToolError


class ToolExecutionResult(BaseModel):
    """Structured result of a single tool execution."""

    model_config = ConfigDict(frozen=True)

    tool_call_id: str
    tool_id: str
    success: bool
    output: Any = None
    error: ToolError | None = None
    state_diff: StateDiff = Field(default_factory=lambda: StateDiff(mutations=[]))
    events_emitted: list[str] = Field(default_factory=list)
    audit_ids: list[str] = Field(default_factory=list)
    pre_state_hash: str = ""
    post_state_hash: str = ""
    authorization_decision: str | None = None
    rollback_token: str | None = None
    idempotent_replay: bool = False
    internal_truth: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def agent_visible(self) -> dict[str, Any]:
        """Return a copy with internal_truth stripped."""
        d = self.model_dump()
        d.pop("internal_truth", None)
        return d
