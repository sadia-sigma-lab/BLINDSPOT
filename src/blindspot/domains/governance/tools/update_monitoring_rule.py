"""update-monitoring-rule tool."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.errors import ToolError


class UpdateMonitoringRuleArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    new_threshold: float | None = None
    enabled: bool | None = None


class UpdateMonitoringRuleTool(PythonTool[UpdateMonitoringRuleArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="update-monitoring-rule", version="1.0.0"),
        display_name="Update Monitoring Rule",
        description="Update a monitoring rule threshold or enabled state. Requires security approval.",
        read_scopes=["monitoring_rules", "resources", "permissions", "approvals"],
        write_scopes=["monitoring_rules", "resources"],
        required_permissions=["update-monitoring-rule"],
        requires_approval=True,
        approval_action="update-monitoring-rule",
        side_effect_level="high",
        reversible=True,
    )
    args_model = UpdateMonitoringRuleArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        rules = view.get_collection("monitoring_rules") if view.has_scope("monitoring_rules") else {}
        rule = rules.get(args.rule_id, {})
        floor = rule.get("floor_threshold", 0.0)
        if args.new_threshold is not None and args.new_threshold < floor:
            raise ValueError(f"Threshold {args.new_threshold} below floor {floor}")
        return {"rule_id": args.rule_id, "proposed_threshold": args.new_threshold}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        rules = view.get_collection("monitoring_rules") if view.has_scope("monitoring_rules") else {}
        before = dict(rules.get(args.rule_id, {}))
        if not before:
            return MutationPlan()
        floor = before.get("floor_threshold", 0.0)
        if args.new_threshold is not None and args.new_threshold < floor:
            return MutationPlan()  # Blocked at authorization level
        patch = {k: v for k, v in {"threshold": args.new_threshold, "enabled": args.enabled}.items() if v is not None}
        after = {**before, **patch}
        return MutationPlan(operations=[MutationOperation(
            collection="monitoring_rules", entity_id=args.rule_id,
            operation="update", before=before, after=after, changed_fields=list(patch.keys()),
        )])
