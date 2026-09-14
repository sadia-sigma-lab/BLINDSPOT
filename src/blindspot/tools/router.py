"""Tool router — resolves registered tools and dispatches execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff
from blindspot.tools.context import ToolExecutionContext, ToolRuntimeDependencies
from blindspot.tools.errors import ToolError
from blindspot.tools.result import ToolExecutionResult

if TYPE_CHECKING:
    from blindspot.core.action import AgentAction
    from blindspot.tools.base import PythonTool


class ToolRouter:
    """Resolves tool names to registered PythonTool instances and dispatches."""

    def __init__(self, tools: "list[PythonTool]") -> None:
        self._by_name: dict[str, "PythonTool"] = {}
        self._by_canonical: dict[str, "PythonTool"] = {}
        for t in tools:
            self._by_canonical[t.specification.tool_id.canonical()] = t
            self._by_name[t.specification.tool_id.name] = t

    def route(
        self,
        action: "AgentAction",
        state: WorldState,
        context: ToolExecutionContext,
        dependencies: ToolRuntimeDependencies,
    ) -> tuple[WorldState, ToolExecutionResult]:
        name = action.name or ""
        tool = self._by_canonical.get(name) or self._by_name.get(name)
        if tool is None:
            err = ToolError.not_found("tool", name)
            return state, ToolExecutionResult(
                tool_call_id=context.tool_call_id, tool_id=name,
                success=False, error=err,
                pre_state_hash="", post_state_hash="",
            )
        return tool.execute(state, action.arguments, context, dependencies)
