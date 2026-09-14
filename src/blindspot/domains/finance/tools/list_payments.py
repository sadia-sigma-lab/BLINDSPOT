"""list-payments tool for finance domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ListPaymentsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status_filter: str | None = None


class ListPaymentsTool(PythonTool[ListPaymentsArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="finance", name="list-payments", version="1.0.0"),
        display_name="List Payments",
        description="List payment records visible to the actor.",
        read_scopes=["payments", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListPaymentsArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ListPaymentsArgs, context: ToolExecutionContext) -> Any:
        payments = view.get_collection("payments") if view.has_scope("payments") else {}
        result = []
        for pid, p in payments.items():
            if not isinstance(p, dict):
                continue
            if args.status_filter and p.get("status") != args.status_filter:
                continue
            result.append({
                "payment_id": pid,
                "amount_usd": p.get("amount_usd"),
                "status": p.get("status"),
                "purpose": p.get("purpose"),
            })
        return {"payments": result}

    def plan_mutations(self, view: ReadOnlyStateView, args: ListPaymentsArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
