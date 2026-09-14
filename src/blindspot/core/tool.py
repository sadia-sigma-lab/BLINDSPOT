"""Tool abstract interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from blindspot.core.metadata import ComponentMetadata

if TYPE_CHECKING:
    from blindspot.core.state import WorldState
    from blindspot.core.tool_result import ToolResult


class ExecutionContext:
    """Opaque context passed to tool.execute(); extended by the runtime."""

    def __init__(self, session_id: str, actor_id: str, step: int) -> None:
        self.session_id = session_id
        self.actor_id = actor_id
        self.step = step
        self.extra: dict[str, Any] = {}


class Tool(ABC):
    """Abstract interface every benchmark tool must implement."""

    metadata: ComponentMetadata
    read_scopes: set[str] = set()
    write_scopes: set[str] = set()

    @abstractmethod
    def schema(self) -> dict[str, Any]:
        """Return the JSON Schema describing valid arguments."""
        ...

    @abstractmethod
    def execute(
        self,
        state: WorldState,
        actor_id: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> ToolResult:
        """Execute the tool and return a structured result."""
        ...
