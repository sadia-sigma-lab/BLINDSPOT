"""request_approval tool."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.event import EnvironmentEvent
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class RequestApprovalArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approver_id: str
    action: str
    resource_id: str | None = None
    target_id: str | None = None


class RequestApprovalTool(PythonTool[RequestApprovalArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="request-approval", version="1.0.0"),
        display_name="Request Approval",
        description="Create a pending approval request and notify the approver.",
        read_scopes=["approvals", "users"],
        write_scopes=["approvals"],
        side_effect_level="low",
        idempotent=True,
    )
    args_model = RequestApprovalArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: RequestApprovalArgs, context: ToolExecutionContext) -> Any:
        return {"status": "pending", "action": args.action,
                "approver_id": args.approver_id, "resource_id": args.resource_id}

    def plan_mutations(self, view: ReadOnlyStateView, args: RequestApprovalArgs, context: ToolExecutionContext) -> MutationPlan:
        now = datetime.now(tz=timezone.utc).isoformat()
        aid = str(uuid.uuid4())
        record = {
            "entity_id": aid, "schema_version": "1.0.0",
            "created_at": now, "updated_at": now,
            "requester_id": context.actor_id, "approver_id": args.approver_id,
            "action": args.action, "resource_id": args.resource_id,
            "target_id": args.target_id, "scope": {}, "status": "pending",
            "valid_until": None, "evidence": [],
        }
        notify = EnvironmentEvent(
            event_id=str(uuid.uuid4()), event_type="approval_requested",
            trigger_step=context.step + 1,
            payload={"approval_id": aid, "approver_id": args.approver_id,
                     "action": args.action, "requester_id": context.actor_id},
            visible_to_agent=True,
        )
        return MutationPlan(operations=[MutationOperation(
            collection="approvals", entity_id=aid, operation="create", after=record,
        )], events=[notify])
