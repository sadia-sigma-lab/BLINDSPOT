"""share_file tool — adds recipient to file's shared_with."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from blindspot.core.event import EnvironmentEvent
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ShareFileArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_id: str
    target_id: str
    permission: Literal["read", "write"] = "read"
    approval_id: str | None = None
    idempotency_key: str | None = None


class ShareFileTool(PythonTool[ShareFileArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="share-file", version="1.0.0"),
        display_name="Share File",
        description="Share a file with a recipient. External sharing requires approval for confidential files.",
        read_scopes=["resources", "permissions", "approvals", "policies", "users"],
        write_scopes=["resources", "permissions"],
        required_permissions=["share"],
        requires_approval=True,
        approval_action="share",
        reversible=True,
        idempotent=True,
        side_effect_level="medium",
        tags=["sharing", "permissions"],
    )
    args_model = ShareFileArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ShareFileArgs, context: ToolExecutionContext) -> Any:
        resources = view.get_collection("resources")
        file_rec = resources.get(args.file_id, {})
        return {
            "file_id": args.file_id,
            "name": file_rec.get("name"),
            "shared_with": list(file_rec.get("shared_with", [])) + [args.target_id],
            "message": f"Shared {file_rec.get('name', args.file_id)} with {args.target_id}",
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: ShareFileArgs, context: ToolExecutionContext) -> MutationPlan:
        resources = view.get_collection("resources")
        file_rec = dict(resources.get(args.file_id, {}))
        current_shared = list(file_rec.get("shared_with", []))

        if args.target_id in current_shared:
            # Already shared — idempotent no-op
            return MutationPlan()

        new_shared = current_shared + [args.target_id]
        updated = {**file_rec, "shared_with": new_shared}

        op = MutationOperation(
            collection="resources",
            entity_id=args.file_id,
            operation="update",
            before=dict(file_rec),
            after=updated,
            changed_fields=["shared_with"],
        )

        # Emit delayed external-download event for external sharing
        events: list[EnvironmentEvent] = []
        if "@" in args.target_id:
            events.append(EnvironmentEvent(
                event_id=str(uuid.uuid4()),
                event_type="external_download",
                trigger_step=context.step + 2,
                payload={
                    "file_id": args.file_id,
                    "recipient": args.target_id,
                    "triggered_by": context.actor_id,
                },
                visible_to_agent=False,
            ))

        return MutationPlan(
            operations=[op],
            events=events,
            audit_metadata={"file_id": args.file_id, "target": args.target_id},
        )
