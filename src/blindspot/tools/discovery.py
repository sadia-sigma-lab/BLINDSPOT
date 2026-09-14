"""Tool discovery service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blindspot.core.scenario import ScenarioSpec
    from blindspot.core.state import WorldState
    from blindspot.tools.base import PythonTool


class ToolDiscoveryService:
    """Returns the tool schemas visible to a specific actor in a scenario."""

    def __init__(self, tools: list["PythonTool"]) -> None:
        self._tools = tools

    def list_tools(
        self,
        *,
        actor_id: str,
        scenario: "ScenarioSpec",
        state: "WorldState",
    ) -> list[dict[str, Any]]:
        """Return agent-visible tool schemas filtered by visibility and deprecation."""
        from blindspot.tools.visibility import is_visible_to_agent
        result = []
        for t in self._tools:
            if not is_visible_to_agent(t.specification):
                continue
            result.append(t.schema())
        return result

    def get_tool(self, name: str) -> "PythonTool | None":
        for t in self._tools:
            if (
                t.specification.tool_id.name == name
                or t.specification.tool_id.canonical() == name
            ):
                return t
        return None
