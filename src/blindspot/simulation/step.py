"""Raw simulation step schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.agents.response import AgentResponse
from blindspot.core.action import AgentAction
from blindspot.parsing.base import ParseResult
from blindspot.prompting.builder import PromptArtifact


class RawSimulationStep(BaseModel):
    """Immutable record of one complete simulation step."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    episode_id: str
    scenario_id: str
    session_id: str
    step: int
    global_step: int
    acting_actor_id: str
    observation: dict[str, Any]
    prompt_artifact: PromptArtifact | None = None
    raw_model_response: AgentResponse | None = None
    parse_result: ParseResult = Field(default_factory=lambda: ParseResult(success=False, parser_id="none"))
    selected_action: AgentAction | None = None
    tool_execution_result: dict[str, Any] | None = None
    attack_trace_refs: list[str] = Field(default_factory=list)
    events_processed: list[str] = Field(default_factory=list)
    pre_state_hash: str = ""
    post_state_hash: str = ""
    token_usage: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = None
    termination_signals: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
