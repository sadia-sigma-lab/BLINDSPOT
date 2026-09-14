"""Optional @tool decorator for function-style tool authoring."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification

ArgsT = TypeVar("ArgsT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class FunctionTool(PythonTool):
    """Wraps a plain function into a PythonTool."""

    def __init__(
        self,
        spec: ToolSpecification,
        args_model: type[BaseModel],
        output_model: type[BaseModel],
        read_fn: Callable,
        plan_fn: Callable,
    ) -> None:
        self.specification = spec
        self.args_model = args_model
        self.output_model = output_model
        self._read_fn = read_fn
        self._plan_fn = plan_fn

    def read(self, view, args, context):
        return self._read_fn(view, args, context)

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return self._plan_fn(view, args, context)


def tool(
    *,
    tool_id: str,
    description: str,
    args_model: type[BaseModel],
    output_model: type[BaseModel] | None = None,
    read_scopes: set[str],
    write_scopes: set[str],
    side_effect_level: str,
    requires_approval: bool = False,
    approval_action: str | None = None,
    reversible: bool = False,
    idempotent: bool = False,
    tags: list[str] | None = None,
    plan_fn: Callable | None = None,
) -> Callable:
    """Decorator that wraps a read function into a PythonTool."""
    from blindspot.core.identifiers import ComponentID

    def decorator(fn: Callable) -> FunctionTool:
        cid = ComponentID.parse(tool_id)
        spec = ToolSpecification(
            tool_id=cid,
            display_name=cid.name.replace("-", " ").title(),
            description=description,
            read_scopes=sorted(read_scopes),
            write_scopes=sorted(write_scopes),
            requires_approval=requires_approval,
            approval_action=approval_action,
            reversible=reversible,
            idempotent=idempotent,
            side_effect_level=side_effect_level,  # type: ignore[arg-type]
            tags=tags or [],
        )

        def _no_mutations(view, args, context) -> MutationPlan:
            return MutationPlan()

        return FunctionTool(
            spec=spec,
            args_model=args_model,
            output_model=output_model or BaseModel,
            read_fn=fn,
            plan_fn=plan_fn or _no_mutations,
        )

    return decorator
