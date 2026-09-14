"""Agent action contract."""

from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict


class AgentAction(BaseModel):
    """An action emitted by an actor in response to an observation."""

    model_config = ConfigDict(frozen=True)

    action_id: str
    action_type: Literal[
        "tool_call",
        "message",
        "ask_user",
        "request_approval",
        "refuse",
        "escalate",
        "rollback",
        "no_op",
    ]
    name: str | None = None
    arguments: dict[str, Any] = {}
    content: str | None = None
