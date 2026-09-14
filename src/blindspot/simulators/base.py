"""Abstract actor simulator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.action import AgentAction

if TYPE_CHECKING:
    from blindspot.core.observation import Observation
    from blindspot.scenarios.actors import ScenarioActorSpec
    from blindspot.scenarios.schema import FullScenarioSpec
    from blindspot.simulation.context import SimulationContext


class SimulatorConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    simulator_id: str
    actor_id: str
    adapter_id: str = "scripted"
    model_name: str | None = None
    scripted_policy_id: str | None = None
    temperature: float = 0.0
    max_actions: int | None = None
    visibility_profile: str = "default"
    behavior_parameters: dict[str, Any] = Field(default_factory=dict)


class ActorSimulator(ABC):
    """Abstract base for all actor simulators."""

    @abstractmethod
    def initialize(
        self,
        scenario: "FullScenarioSpec",
        actor: "ScenarioActorSpec",
        seed: int,
    ) -> None:
        ...

    @abstractmethod
    def act(
        self,
        observation: "Observation",
        context: "SimulationContext",
    ) -> AgentAction:
        ...
