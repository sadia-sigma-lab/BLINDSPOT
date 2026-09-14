"""list_files tool — returns visible file metadata."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ListFilesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    classification_filter: str | None = None


class ListFilesOutput(BaseModel):
    files: list[dict[str, Any]]


class ListFilesTool(PythonTool[ListFilesArgs, ListFilesOutput]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="list-files", version="1.0.0"),
        display_name="List Files",
        description="List all files visible to the actor. Does not return content.",
        read_scopes=["resources", "permissions"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListFilesArgs
    output_model = ListFilesOutput

    def read(self, view: ReadOnlyStateView, args: ListFilesArgs, context: ToolExecutionContext) -> Any:
        resources = view.get_collection("resources")
        files = []
        for fid, f in resources.items():
            if not isinstance(f, dict):
                continue
            if args.classification_filter and f.get("classification") != args.classification_filter:
                continue
            files.append({
                "file_id": fid,
                "name": f.get("name"),
                "owner_id": f.get("owner_id"),
                "classification": f.get("classification"),
                "tags": f.get("tags", []),
            })
        return {"files": sorted(files, key=lambda x: x["file_id"])}

    def plan_mutations(self, view: ReadOnlyStateView, args: ListFilesArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
