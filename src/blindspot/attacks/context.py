"""Attack context — what the attacker can observe, bounded by knowledge tier."""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.taxonomy import AttackerKnowledgeTier
from blindspot.core.state import WorldState


class AttackContext(BaseModel):
    """Attacker-visible context at one step, filtered by knowledge tier."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    episode_id: str
    scenario_id: str
    domain_id: str
    step: int
    session_id: str
    seed: int
    current_time: datetime
    target_actor_id: str
    knowledge_tier: AttackerKnowledgeTier
    public_messages: list[dict[str, Any]] = Field(default_factory=list)
    visible_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    visible_tool_results: list[dict[str, Any]] = Field(default_factory=list)
    visible_state: dict[str, Any] = Field(default_factory=dict)
    defense_metadata: dict[str, Any] = Field(default_factory=dict)


# Always-hidden fields that no knowledge tier can see
_ALWAYS_HIDDEN_KEYS = frozenset({"hidden", "grading", "attack_state", "__hidden__"})


def build_attack_context(
    world_state: WorldState,
    knowledge_tier: AttackerKnowledgeTier,
    run_id: str,
    episode_id: str,
    scenario_id: str,
    domain_id: str,
    step: int,
    session_id: str,
    seed: int,
    current_time: datetime,
    target_actor_id: str,
    tool_call_history: list[dict[str, Any]] | None = None,
    tool_result_history: list[dict[str, Any]] | None = None,
    message_history: list[dict[str, Any]] | None = None,
    defense_metadata: dict[str, Any] | None = None,
) -> AttackContext:
    """Build an AttackContext respecting the knowledge tier ceiling."""
    public_messages: list[dict[str, Any]] = []
    visible_tool_calls: list[dict[str, Any]] = []
    visible_tool_results: list[dict[str, Any]] = []
    visible_state: dict[str, Any] = {}
    dm: dict[str, Any] = {}

    # STATIC: no runtime information
    if knowledge_tier == AttackerKnowledgeTier.STATIC:
        pass

    # PUBLIC_RESPONSES: sees agent messages only
    elif knowledge_tier == AttackerKnowledgeTier.PUBLIC_RESPONSES:
        public_messages = copy.deepcopy(message_history or [])

    # TOOL_CALLS: sees tool calls and results
    elif knowledge_tier == AttackerKnowledgeTier.TOOL_CALLS:
        public_messages = copy.deepcopy(message_history or [])
        visible_tool_calls = copy.deepcopy(tool_call_history or [])
        visible_tool_results = copy.deepcopy(tool_result_history or [])

    # PARTIAL_STATE: additionally sees filtered public state
    elif knowledge_tier in (
        AttackerKnowledgeTier.PARTIAL_STATE,
        AttackerKnowledgeTier.DEFENSE_AWARE,
    ):
        public_messages = copy.deepcopy(message_history or [])
        visible_tool_calls = copy.deepcopy(tool_call_history or [])
        visible_tool_results = copy.deepcopy(tool_result_history or [])
        # Project public state with hidden collections stripped
        for k, v in world_state.public.items():
            if k not in _ALWAYS_HIDDEN_KEYS:
                visible_state[k] = copy.deepcopy(v)
        if knowledge_tier == AttackerKnowledgeTier.DEFENSE_AWARE:
            dm = copy.deepcopy(defense_metadata or {})

    # INTERNAL_REASONING: reserved; same as PARTIAL_STATE until LLM judge skill
    elif knowledge_tier == AttackerKnowledgeTier.INTERNAL_REASONING:
        public_messages = copy.deepcopy(message_history or [])
        visible_tool_calls = copy.deepcopy(tool_call_history or [])
        visible_tool_results = copy.deepcopy(tool_result_history or [])
        for k, v in world_state.public.items():
            if k not in _ALWAYS_HIDDEN_KEYS:
                visible_state[k] = copy.deepcopy(v)

    # Enforce: hidden state NEVER visible regardless of tier
    for hk in _ALWAYS_HIDDEN_KEYS:
        visible_state.pop(hk, None)

    return AttackContext(
        run_id=run_id,
        episode_id=episode_id,
        scenario_id=scenario_id,
        domain_id=domain_id,
        step=step,
        session_id=session_id,
        seed=seed,
        current_time=current_time,
        target_actor_id=target_actor_id,
        knowledge_tier=knowledge_tier,
        public_messages=public_messages,
        visible_tool_calls=visible_tool_calls,
        visible_tool_results=visible_tool_results,
        visible_state=visible_state,
        defense_metadata=dm,
    )
