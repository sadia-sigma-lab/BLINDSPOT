"""Tool implementations for the minimal workspace domain."""

from __future__ import annotations

from typing import Any

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata
from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff, StateMutation
from blindspot.core.tool import ExecutionContext, Tool
from blindspot.core.tool_result import ToolResult


def _audit(actor_id: str, action: str, detail: str) -> dict[str, Any]:
    return {"actor_id": actor_id, "action": action, "detail": detail}


class ListFilesTool(Tool):
    """List all files visible in the workspace."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="list-files", version="1.0.0"),
        display_name="List Files",
        description="Returns the list of files in the workspace.",
        source_package="examples.minimal_domain",
    )
    read_scopes = {"files"}
    write_scopes: set[str] = set()

    def schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(
        self,
        state: WorldState,
        actor_id: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> ToolResult:
        files = state.public.get("files", {})
        output = [
            {"file_id": fid, "name": meta["name"], "owner_id": meta["owner_id"]}
            for fid, meta in files.items()
        ]
        return ToolResult(
            success=True,
            output=output,
            state_diff=StateDiff(mutations=[]),
            audit_entries=[_audit(actor_id, "list_files", "")],
        )


class ReadFileTool(Tool):
    """Read the content of a file by ID."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="read-file", version="1.0.0"),
        display_name="Read File",
        description="Returns the full content of a file.",
        source_package="examples.minimal_domain",
    )
    read_scopes = {"files"}
    write_scopes: set[str] = set()

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"file_id": {"type": "string"}},
            "required": ["file_id"],
        }

    def execute(
        self,
        state: WorldState,
        actor_id: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> ToolResult:
        file_id = arguments.get("file_id")
        if not file_id:
            return ToolResult(
                success=False,
                error_code="MISSING_ARG",
                error_message="file_id is required",
                state_diff=StateDiff(mutations=[]),
            )
        files = state.public.get("files", {})
        if file_id not in files:
            return ToolResult(
                success=False,
                error_code="FILE_NOT_FOUND",
                error_message=f"File {file_id!r} does not exist",
                state_diff=StateDiff(mutations=[]),
            )
        return ToolResult(
            success=True,
            output=files[file_id],
            state_diff=StateDiff(mutations=[]),
            audit_entries=[_audit(actor_id, "read_file", file_id)],
        )


class ShareFileTool(Tool):
    """Share a file with an email address."""

    metadata = ComponentMetadata(
        component_id=ComponentID(namespace="core", name="share-file", version="1.0.0"),
        display_name="Share File",
        description="Adds a recipient to the file's shared_with list.",
        source_package="examples.minimal_domain",
    )
    read_scopes = {"files"}
    write_scopes = {"files"}

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_id": {"type": "string"},
                "recipient": {"type": "string"},
            },
            "required": ["file_id", "recipient"],
        }

    def execute(
        self,
        state: WorldState,
        actor_id: str,
        arguments: dict[str, Any],
        context: ExecutionContext,
    ) -> ToolResult:
        file_id = arguments.get("file_id")
        recipient = arguments.get("recipient")
        if not file_id or not recipient:
            return ToolResult(
                success=False,
                error_code="MISSING_ARG",
                error_message="file_id and recipient are required",
                state_diff=StateDiff(mutations=[]),
            )
        files = state.public.get("files", {})
        if file_id not in files:
            return ToolResult(
                success=False,
                error_code="FILE_NOT_FOUND",
                error_message=f"File {file_id!r} does not exist",
                state_diff=StateDiff(mutations=[]),
            )
        current_shared = list(files[file_id].get("shared_with", []))
        if recipient in current_shared:
            return ToolResult(
                success=True,
                output={"message": "Already shared", "shared_with": current_shared},
                state_diff=StateDiff(mutations=[]),
            )
        new_shared = current_shared + [recipient]
        mutation = StateMutation(
            path=f"public.files.{file_id}.shared_with",
            operation="replace",
            before=current_shared,
            after=new_shared,
        )
        return ToolResult(
            success=True,
            output={"message": f"Shared with {recipient}", "shared_with": new_shared},
            state_diff=StateDiff(mutations=[mutation]),
            audit_entries=[_audit(actor_id, "share_file", f"{file_id} -> {recipient}")],
        )
