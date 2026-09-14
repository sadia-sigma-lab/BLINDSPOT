"""read_message tool."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ReadMessageArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str


class ReadMessageTool(PythonTool[ReadMessageArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="read-message", version="1.0.0"),
        display_name="Read Message",
        description="Return the content of a message. Does not expose hidden injection labels.",
        read_scopes=["messages"],
        write_scopes=[],
        side_effect_level="read",
        idempotent=True,
    )
    args_model = ReadMessageArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ReadMessageArgs, context: ToolExecutionContext) -> Any:
        messages = view.get_collection("messages")
        msg = messages.get(args.message_id)
        if msg is None:
            raise ValueError(f"Message {args.message_id!r} not found")
        # Project: omit any hidden labels
        return {
            "message_id": args.message_id,
            "sender_id": msg.get("sender_id"),
            "subject": msg.get("subject"),
            "body": msg.get("body"),
            "trust_level": msg.get("trust_level"),
            "attachment_ids": msg.get("attachment_ids", []),
        }

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
