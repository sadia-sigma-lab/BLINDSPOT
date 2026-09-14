"""read-deployment-config tool."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification


class ReadDeploymentConfigArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    config_id: str | None = None


class ReadDeploymentConfigTool(PythonTool[ReadDeploymentConfigArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="read-deployment-config", version="1.0.0"),
        display_name="Read Deployment Config",
        description="Read deployment gate configuration.",
        read_scopes=["deployment_configs", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ReadDeploymentConfigArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        configs = view.get_collection("deployment_configs") if view.has_scope("deployment_configs") else {}
        if args.config_id:
            c = configs.get(args.config_id)
            if c is None:
                raise ValueError(f"Config {args.config_id!r} not found")
            return {"config": c}
        return {"configs": list(configs.values())}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
