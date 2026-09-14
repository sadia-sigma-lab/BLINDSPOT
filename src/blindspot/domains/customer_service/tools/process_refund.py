"""process-refund tool for customer service domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ProcessRefundArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str
    refund_amount: float


class ProcessRefundTool(PythonTool[ProcessRefundArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="process-refund", version="1.0.0"),
        display_name="Process Refund",
        description="Process a refund for a delivered order.",
        read_scopes=["orders", "accounts", "approvals", "resources"],
        write_scopes=["orders", "resources"],
        required_permissions=["refund"],
        requires_approval=True,
        approval_action="refund",
        side_effect_level="high",
    )
    args_model = ProcessRefundArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ProcessRefundArgs, context: ToolExecutionContext) -> Any:
        orders = view.get_collection("orders") if view.has_scope("orders") else {}
        order = orders.get(args.order_id)
        if order is None:
            raise ValueError(f"Order {args.order_id!r} not found")
        if not isinstance(order, dict):
            raise ValueError(f"Order {args.order_id!r} has unexpected format")
        total = order.get("total_usd", 0.0) or 0.0
        eligible = order.get("eligible_for_refund", False)
        if not eligible:
            raise ValueError(f"Order {args.order_id!r} is not eligible for a refund")
        if args.refund_amount > total:
            raise ValueError(
                f"Refund amount {args.refund_amount} exceeds order total {total}"
            )
        return {
            "order_id": args.order_id,
            "refund_amount": args.refund_amount,
            "order_total": total,
            "preview": "refund_pending",
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: ProcessRefundArgs, context: ToolExecutionContext) -> MutationPlan:
        orders = view.get_collection("orders") if view.has_scope("orders") else {}
        order = orders.get(args.order_id)
        if order is None or not isinstance(order, dict):
            return MutationPlan()
        updated = {**order, "refund_amount": args.refund_amount, "status": "refunded"}
        return MutationPlan(operations=[MutationOperation(
            collection="orders",
            entity_id=args.order_id,
            operation="update",
            before=dict(order),
            after=updated,
            changed_fields=["refund_amount", "status"],
        )])
