"""Attack lifecycle hook definitions and effect contracts."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AttackHook(str, Enum):
    BEFORE_SESSION = "before_session"
    AFTER_SESSION = "after_session"
    BEFORE_USER_MESSAGE = "before_user_message"
    AFTER_USER_MESSAGE = "after_user_message"
    BEFORE_OBSERVATION = "before_observation"
    AFTER_OBSERVATION = "after_observation"
    BEFORE_ACTION = "before_action"
    AFTER_ACTION = "after_action"
    BEFORE_TOOL = "before_tool"
    AFTER_TOOL = "after_tool"
    BEFORE_EVENT = "before_event"
    AFTER_EVENT = "after_event"
    BEFORE_MEMORY_WRITE = "before_memory_write"
    AFTER_MEMORY_WRITE = "after_memory_write"
    ON_EPISODE_END = "on_episode_end"


class AttackEffect(BaseModel):
    """All modifications an attack may produce at one lifecycle hook."""

    model_config = ConfigDict(frozen=True)

    messages_to_add: list[dict[str, Any]] = Field(default_factory=list)
    observations_to_modify: list[dict[str, Any]] = Field(default_factory=list)
    tool_results_to_modify: list[dict[str, Any]] = Field(default_factory=list)
    memory_records_to_add: list[dict[str, Any]] = Field(default_factory=list)
    events_to_emit: list[dict[str, Any]] = Field(default_factory=list)
    metadata_updates: dict[str, Any] = Field(default_factory=dict)
    no_op: bool = False

    @classmethod
    def noop(cls) -> "AttackEffect":
        return cls(no_op=True)

    def is_empty(self) -> bool:
        return (
            not self.messages_to_add
            and not self.observations_to_modify
            and not self.tool_results_to_modify
            and not self.memory_records_to_add
            and not self.events_to_emit
            and not self.metadata_updates
        )

    def validate_effect(self) -> list[str]:
        """Return list of validation error strings (empty = valid)."""
        errors: list[str] = []
        for msg in self.messages_to_add:
            if not isinstance(msg, dict):
                errors.append("messages_to_add must contain dicts")
            elif "content" not in msg and "body" not in msg:
                errors.append("message entry missing 'content' or 'body' field")
        return errors
