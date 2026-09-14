"""list_messages tool."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ListMessagesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trust_level_filter: str | None = None


class ListMessagesTool(PythonTool[ListMessagesArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="list-messages", version="1.0.0"),
        display_name="List Messages",
        description="List message metadata visible to the actor.",
        read_scopes=["messages"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListMessagesArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ListMessagesArgs, context: ToolExecutionContext) -> Any:
        messages = view.get_collection("messages")
        result = []
        for mid, m in messages.items():
            if not isinstance(m, dict):
                continue
            if args.trust_level_filter and m.get("trust_level") != args.trust_level_filter:
                continue
            if context.actor_id not in m.get("visible_to", [m.get("sender_id")]):
                continue
            result.append({"message_id": mid, "subject": m.get("subject"),
                           "sender_id": m.get("sender_id"), "trust_level": m.get("trust_level")})
        return {"messages": result}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
