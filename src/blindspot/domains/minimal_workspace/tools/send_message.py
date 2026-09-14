"""send_message tool."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.errors import ToolError
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class SendMessageArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recipient_ids: list[str]
    subject: str
    body: str
    attachment_ids: list[str] = []
    idempotency_key: str | None = None


class SendMessageTool(PythonTool[SendMessageArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="send-message", version="1.0.0"),
        display_name="Send Message",
        description="Send a message to one or more recipients.",
        read_scopes=["messages", "users", "resources"],
        write_scopes=["messages"],
        side_effect_level="medium",
        idempotent=True,
    )
    args_model = SendMessageArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: SendMessageArgs, context: ToolExecutionContext) -> Any:
        return {"message_id": str(uuid.uuid4()), "status": "sent",
                "subject": args.subject, "recipients": args.recipient_ids}

    def plan_mutations(self, view: ReadOnlyStateView, args: SendMessageArgs, context: ToolExecutionContext) -> MutationPlan:
        # Validate attachments exist
        if args.attachment_ids:
            resources = view.get_collection("resources")
            for att_id in args.attachment_ids:
                if att_id not in resources:
                    raise ValueError(f"Attachment {att_id!r} not found")

        now = datetime.now(tz=timezone.utc).isoformat()
        mid = str(uuid.uuid4())
        record = {
            "entity_id": mid, "schema_version": "1.0.0",
            "created_at": now, "updated_at": now,
            "sender_id": context.actor_id,
            "recipient_ids": args.recipient_ids,
            "subject": args.subject, "body": args.body,
            "attachment_ids": args.attachment_ids,
            "trust_level": "internal", "channel": "tool",
            "visible_to": [context.actor_id] + args.recipient_ids,
        }
        return MutationPlan(operations=[MutationOperation(
            collection="messages", entity_id=mid, operation="create", after=record,
        )])
