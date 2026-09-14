"""Governance inspect-policy tool."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification


class GovInspectPolicyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str | None = None


class GovInspectPolicyTool(PythonTool[GovInspectPolicyArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="gov-inspect-policy", version="1.0.0"),
        display_name="Inspect Policy",
        description="Return governance policy information.",
        read_scopes=["policies"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = GovInspectPolicyArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        policies = view.get_collection("policies")
        if args.policy_id:
            pol = policies.get(args.policy_id)
            if pol is None:
                raise ValueError(f"Policy {args.policy_id!r} not found")
            return {"policies": [self._proj(args.policy_id, pol)]}
        return {"policies": [self._proj(pid, p) for pid, p in policies.items()]}

    def _proj(self, pid, pol):
        if isinstance(pol, dict):
            return {"policy_id": pid, "title": pol.get("title"),
                    "rules": [{"rule_id": r.get("rule_id"), "effect": r.get("effect"),
                               "description": r.get("description")} for r in pol.get("rules", [])]}
        return {"policy_id": pid}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
