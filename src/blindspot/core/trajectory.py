"""Trajectory record contracts."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.action import AgentAction
from blindspot.core.observation import Observation
from blindspot.core.state_diff import StateDiff
from blindspot.core.tool_result import ToolResult


class TrajectoryStep(BaseModel):
    """Immutable record of one agent-environment interaction step."""

    model_config = ConfigDict(frozen=True)

    episode_id: str
    step: int
    session_id: str
    observation: Observation
    raw_agent_output: str | dict[str, Any]
    parsed_action: AgentAction
    tool_result: ToolResult | None
    pre_state_hash: str
    post_state_hash: str
    state_diff: StateDiff
    events_processed: list[str]
    metadata: dict[str, Any] = {}
