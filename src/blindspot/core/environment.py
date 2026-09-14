"""BenchmarkEnvironment abstract interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blindspot.core.action import AgentAction
    from blindspot.core.observation import Observation


class BenchmarkEnvironment(ABC):
    """Abstract environment interface compatible with future Gymnasium wrapping."""

    @abstractmethod
    def reset(
        self,
        *,
        scenario_id: str,
        seed: int,
    ) -> tuple[Observation, dict[str, Any]]:
        """Reset to a fresh episode; return initial observation and info dict."""
        ...

    @abstractmethod
    def step(
        self,
        action: AgentAction,
    ) -> tuple[
        Observation,
        dict[str, float],
        dict[str, float],
        bool,
        bool,
        dict[str, Any],
    ]:
        """Apply action; return (obs, rewards, costs, terminated, truncated, info)."""
        ...

    @abstractmethod
    def snapshot(self) -> str:
        """Persist current state; return snapshot ID."""
        ...

    @abstractmethod
    def restore(self, snapshot_id: str) -> None:
        """Restore to a previously saved snapshot."""
        ...
