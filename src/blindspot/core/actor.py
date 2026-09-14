"""Actor abstract interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from blindspot.core.action import AgentAction
from blindspot.core.metadata import ComponentMetadata
from blindspot.core.observation import Observation


@dataclass
class ActorContext:
    """Runtime context available to an actor when producing an action."""

    session_id: str
    step: int
    scenario_id: str
    extra: dict[str, Any] = field(default_factory=dict)


class Actor(ABC):
    """Abstract interface every benchmark actor must implement."""

    metadata: ComponentMetadata

    @abstractmethod
    def act(
        self,
        observation: Observation,
        context: ActorContext,
    ) -> AgentAction:
        """Produce an action given the current observation."""
        ...
