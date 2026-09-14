"""Abstract intervention interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.action import AgentAction
from blindspot.core.metadata import ComponentMetadata


class InterventionContext(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: str
    episode_id: str
    step: int
    actor_id: str
    seed: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class InterventionApplication(BaseModel):
    model_config = ConfigDict(frozen=True)
    intervention_id: str
    source_step: int
    replaced_action: AgentAction | None = None
    inserted_actions: list[AgentAction] = Field(default_factory=list)
    tool_constraints: dict[str, Any] = Field(default_factory=dict)
    prompt_modifications: list[str] = Field(default_factory=list)
    expected_cost_components: dict[str, float] = Field(default_factory=dict)


class Intervention(ABC):
    """Abstract benchmark intervention."""

    metadata: ComponentMetadata

    @abstractmethod
    def is_applicable(
        self,
        snapshot: dict[str, Any],
        source_action: AgentAction,
        scenario: Any,
    ) -> bool:
        ...

    @abstractmethod
    def apply(
        self,
        snapshot: dict[str, Any],
        source_action: AgentAction,
        context: InterventionContext,
    ) -> InterventionApplication:
        ...
