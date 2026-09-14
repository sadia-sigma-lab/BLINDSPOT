"""Observation contract — what the agent sees at each step."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class Observation(BaseModel):
    """Structured view of the environment delivered to the agent."""

    model_config = ConfigDict(frozen=True)

    step: int
    session_id: str
    messages: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    notifications: list[dict[str, Any]]
    available_tools: list[dict[str, Any]]
    metadata: dict[str, Any] = {}
