"""read_file tool."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.errors import ToolError
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ReadFileArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_id: str


class ReadFileTool(PythonTool[ReadFileArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="read-file", version="1.0.0"),
        display_name="Read File",
        description="Return the content and metadata of a file. Requires read permission.",
        read_scopes=["resources", "permissions"],
        write_scopes=[],
        required_permissions=["read"],
        side_effect_level="read",
        idempotent=True,
    )
    args_model = ReadFileArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ReadFileArgs, context: ToolExecutionContext) -> Any:
        resources = view.get_collection("resources")
        file_rec = resources.get(args.file_id)
        if file_rec is None:
            raise ValueError(f"File {args.file_id!r} not found")
        # Return projected view — never expose hidden grading labels
        return {
            "file_id": args.file_id,
            "name": file_rec.get("name"),
            "content": file_rec.get("content", ""),
            "classification": file_rec.get("classification"),
            "owner_id": file_rec.get("owner_id"),
            "shared_with": file_rec.get("shared_with", []),
            "tags": file_rec.get("tags", []),
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: ReadFileArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
