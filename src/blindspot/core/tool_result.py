"""Tool result contract."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.state_diff import StateDiff


class ToolResult(BaseModel):
    """Structured result returned by every tool execution."""

    model_config = ConfigDict(frozen=True)

    success: bool
    output: Any = None
    error_code: str | None = None
    error_message: str | None = None
    state_diff: StateDiff
    emitted_events: list[dict[str, Any]] = []
    audit_entries: list[dict[str, Any]] = []
