"""list-pipelines tool."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView
from blindspot.tools.context import ToolExecutionContext


class ListPipelinesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    environment_filter: str | None = None
    status_filter: str | None = None


class ListPipelinesTool(PythonTool[ListPipelinesArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="software-ops", name="list-pipelines", version="1.0.0"),
        display_name="List Pipelines",
        description="List CI/CD pipelines visible to the actor.",
        read_scopes=["pipelines", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListPipelinesArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ListPipelinesArgs, context: ToolExecutionContext) -> Any:
        pipelines = view.get_collection("pipelines") if view.has_scope("pipelines") else {}
        result = []
        for pid, p in pipelines.items():
            if not isinstance(p, dict):
                continue
            if args.environment_filter and p.get("deployment_target") != args.environment_filter:
                continue
            if args.status_filter and p.get("status") != args.status_filter:
                continue
            result.append({
                "pipeline_id": pid,
                "name": p.get("name"),
                "status": p.get("status"),
                "deployment_target": p.get("deployment_target"),
                "requires_approval": p.get("requires_approval", False),
            })
        return {"pipelines": result}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
