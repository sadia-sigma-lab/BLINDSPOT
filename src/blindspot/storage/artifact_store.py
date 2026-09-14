"""Abstract artifact store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class ArtifactStore(ABC):
    """Minimal interface for persisting benchmark artifacts."""

    @abstractmethod
    def write_json(self, relative_path: str, data: dict[str, Any]) -> str:
        """Write a JSON object; return the resolved absolute path."""
        ...

    @abstractmethod
    def write_jsonl(self, relative_path: str, records: Iterable[dict[str, Any]]) -> str:
        """Append JSON lines; return the resolved absolute path."""
        ...

    @abstractmethod
    def read_json(self, relative_path: str) -> dict[str, Any]:
        """Read a JSON object from storage."""
        ...

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """Return True if the artifact at relative_path exists."""
        ...
