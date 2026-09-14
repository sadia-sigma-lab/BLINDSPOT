"""read-payment tool."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ReadPaymentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_id: str


class ReadPaymentTool(PythonTool[ReadPaymentArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="finance", name="read-payment", version="1.0.0"),
        display_name="Read Payment",
        description="Read details of a payment record.",
        read_scopes=["payments", "resources"],
        write_scopes=[],
        required_permissions=["read"],
        side_effect_level="read",
        idempotent=True,
    )
    args_model = ReadPaymentArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ReadPaymentArgs, context: ToolExecutionContext) -> Any:
        payments = view.get_collection("payments") if view.has_scope("payments") else {}
        p = payments.get(args.payment_id)
        if p is None:
            raise ValueError(f"Payment {args.payment_id!r} not found")
        return {k: v for k, v in p.items() if not k.startswith("__")}

    def plan_mutations(self, view: ReadOnlyStateView, args: ReadPaymentArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
