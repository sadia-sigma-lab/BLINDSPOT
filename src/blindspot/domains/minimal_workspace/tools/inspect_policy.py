"""inspect_policy tool."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class InspectPolicyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str | None = None


class InspectPolicyTool(PythonTool[InspectPolicyArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="inspect-policy", version="1.0.0"),
        display_name="Inspect Policy",
        description="Return human-readable policy information. Never exposes hidden grading.",
        read_scopes=["policies"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = InspectPolicyArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: InspectPolicyArgs, context: ToolExecutionContext) -> Any:
        policies = view.get_collection("policies")
        if args.policy_id:
            pol = policies.get(args.policy_id)
            if pol is None:
                raise ValueError(f"Policy {args.policy_id!r} not found")
            return {"policies": [self._project_policy(args.policy_id, pol)]}
        return {"policies": [self._project_policy(pid, p) for pid, p in policies.items()]}

    def _project_policy(self, pid: str, pol: Any) -> dict:
        if isinstance(pol, dict):
            rules = [{"rule_id": r.get("rule_id"), "effect": r.get("effect"),
                      "description": r.get("description")}
                     for r in pol.get("rules", [])]
            return {"policy_id": pid, "title": pol.get("title"), "rules": rules}
        return {"policy_id": pid}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
