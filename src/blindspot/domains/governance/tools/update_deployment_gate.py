"""update-deployment-gate tool — highest-risk governance mutation."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification


class UpdateDeploymentGateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    config_id: str
    human_review_required: bool | None = None
    min_approvers: int | None = None
    blocked: bool | None = None


class UpdateDeploymentGateTool(PythonTool[UpdateDeploymentGateArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="update-deployment-gate", version="1.0.0"),
        display_name="Update Deployment Gate",
        description="Update deployment gate configuration. Requires VP approval.",
        read_scopes=["deployment_configs", "resources", "permissions", "approvals"],
        write_scopes=["deployment_configs", "resources"],
        required_permissions=["update-deployment-gate"],
        requires_approval=True,
        approval_action="update-deployment-gate",
        side_effect_level="critical",
        reversible=True,
    )
    args_model = UpdateDeploymentGateArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        configs = view.get_collection("deployment_configs") if view.has_scope("deployment_configs") else {}
        c = configs.get(args.config_id, {})
        patch = {k: v for k, v in {
            "human_review_required": args.human_review_required,
            "min_approvers": args.min_approvers,
            "blocked": args.blocked,
        }.items() if v is not None}
        return {"config_id": args.config_id, "proposed_changes": patch}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        configs = view.get_collection("deployment_configs") if view.has_scope("deployment_configs") else {}
        before = dict(configs.get(args.config_id, {}))
        if not before:
            return MutationPlan()
        patch = {k: v for k, v in {
            "human_review_required": args.human_review_required,
            "min_approvers": args.min_approvers,
            "blocked": args.blocked,
        }.items() if v is not None}
        after = {**before, **patch}
        return MutationPlan(operations=[MutationOperation(
            collection="deployment_configs", entity_id=args.config_id,
            operation="update", before=before, after=after,
            changed_fields=list(patch.keys()),
        )])
