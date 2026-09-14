"""read-approval-matrix tool."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification


class ReadApprovalMatrixArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    matrix_id: str | None = None


class ReadApprovalMatrixTool(PythonTool[ReadApprovalMatrixArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="read-approval-matrix", version="1.0.0"),
        display_name="Read Approval Matrix",
        description="Read approval matrix configuration.",
        read_scopes=["approval_matrices", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ReadApprovalMatrixArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        matrices = view.get_collection("approval_matrices") if view.has_scope("approval_matrices") else {}
        if args.matrix_id:
            m = matrices.get(args.matrix_id)
            if m is None:
                raise ValueError(f"Matrix {args.matrix_id!r} not found")
            return {"matrix": m}
        return {"matrices": list(matrices.values())}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
