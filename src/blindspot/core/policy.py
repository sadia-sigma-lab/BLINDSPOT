"""Policy abstract interface (placeholder for future RL/RLHF policies)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from blindspot.core.metadata import ComponentMetadata

if TYPE_CHECKING:
    from blindspot.core.action import AgentAction
    from blindspot.core.observation import Observation


class Policy(ABC):
    """Abstract policy interface for actor decision-making strategies."""

    metadata: ComponentMetadata

    @abstractmethod
    def select_action(
        self,
        observation: Observation,
        context: dict[str, Any],
    ) -> AgentAction:
        """Select an action given an observation and context."""
        ...

    def update(self, experience: dict[str, Any]) -> None:
        """Optional: update policy parameters from experience (for RL)."""
