"""cancel-order tool for customer service domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView

_CANCELLABLE_STATUSES = frozenset({"pending", "processing"})
_NON_CANCELLABLE_STATUSES = frozenset({"delivered", "cancelled", "refunded"})


class CancelOrderArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str
    reason: str = "customer_request"


class CancelOrderTool(PythonTool[CancelOrderArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="cancel-order", version="1.0.0"),
        display_name="Cancel Order",
        description="Cancel a pending or processing order.",
        read_scopes=["orders", "resources", "permissions"],
        write_scopes=["orders", "resources"],
        required_permissions=["cancel"],
        side_effect_level="medium",
        reversible=True,
    )
    args_model = CancelOrderArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: CancelOrderArgs, context: ToolExecutionContext) -> Any:
        orders = view.get_collection("orders") if view.has_scope("orders") else {}
        order = orders.get(args.order_id)
        if order is None:
            raise ValueError(f"Order {args.order_id!r} not found")
        status = order.get("status", "") if isinstance(order, dict) else ""
        if status in _NON_CANCELLABLE_STATUSES:
            raise ValueError(
                f"Order {args.order_id!r} cannot be cancelled: current status is {status!r}"
            )
        if status not in _CANCELLABLE_STATUSES:
            raise ValueError(
                f"Order {args.order_id!r} cannot be cancelled: status {status!r} is not cancellable"
            )
        return {
            "order_id": args.order_id,
            "previous_status": status,
            "new_status": "cancelled",
            "reason": args.reason,
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: CancelOrderArgs, context: ToolExecutionContext) -> MutationPlan:
        orders = view.get_collection("orders") if view.has_scope("orders") else {}
        order = orders.get(args.order_id)
        if order is None or not isinstance(order, dict):
            return MutationPlan()
        status = order.get("status", "")
        if status not in _CANCELLABLE_STATUSES:
            return MutationPlan()
        updated = {**order, "status": "cancelled"}
        return MutationPlan(operations=[MutationOperation(
            collection="orders",
            entity_id=args.order_id,
            operation="update",
            before=dict(order),
            after=updated,
            changed_fields=["status"],
        )])
