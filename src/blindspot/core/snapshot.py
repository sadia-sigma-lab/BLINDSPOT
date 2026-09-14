"""Snapshot contract for runtime state persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class RuntimeState(BaseModel):
    """Full serializable runtime state captured at a single point in time."""

    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    scenario_id: str
    session_id: str
    step: int
    world_state: dict[str, Any]
    event_queue: list[dict[str, Any]]
    rng_state: dict[str, Any]
    plugin_versions: dict[str, str]
    package_version: str


class SnapshotManager(ABC):
    """Abstract interface for creating and restoring runtime snapshots."""

    @abstractmethod
    def create(self, runtime_state: RuntimeState) -> str:
        """Persist the snapshot; return its ID."""
        ...

    @abstractmethod
    def restore(self, snapshot_id: str) -> RuntimeState:
        """Load and return the runtime state for the given snapshot ID."""
        ...
