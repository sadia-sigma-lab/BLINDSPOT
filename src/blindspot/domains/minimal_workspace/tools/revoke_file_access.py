"""revoke_file_access tool — removes a recipient from shared_with."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class RevokeFileAccessArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_id: str
    target_id: str


class RevokeFileAccessTool(PythonTool[RevokeFileAccessArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="revoke-file-access", version="1.0.0"),
        display_name="Revoke File Access",
        description="Remove a recipient from a file's shared_with list.",
        read_scopes=["resources", "permissions"],
        write_scopes=["resources"],
        required_permissions=["share"],
        side_effect_level="medium",
    )
    args_model = RevokeFileAccessArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: RevokeFileAccessArgs, context: ToolExecutionContext) -> Any:
        resources = view.get_collection("resources")
        file_rec = resources.get(args.file_id, {})
        new_shared = [r for r in file_rec.get("shared_with", []) if r != args.target_id]
        return {"file_id": args.file_id, "shared_with": new_shared,
                "message": f"Revoked access for {args.target_id}"}

    def plan_mutations(self, view: ReadOnlyStateView, args: RevokeFileAccessArgs, context: ToolExecutionContext) -> MutationPlan:
        resources = view.get_collection("resources")
        file_rec = dict(resources.get(args.file_id, {}))
        current_shared = list(file_rec.get("shared_with", []))
        if args.target_id not in current_shared:
            return MutationPlan()
        new_shared = [r for r in current_shared if r != args.target_id]
        updated = {**file_rec, "shared_with": new_shared}
        return MutationPlan(operations=[MutationOperation(
            collection="resources", entity_id=args.file_id, operation="update",
            before=dict(file_rec), after=updated, changed_fields=["shared_with"],
        )])
