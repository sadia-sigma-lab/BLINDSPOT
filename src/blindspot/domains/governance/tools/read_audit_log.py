"""read-audit-log tool — audit logs are append-only."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification


class ReadAuditLogArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = 20
    actor_filter: str | None = None


class ReadAuditLogTool(PythonTool[ReadAuditLogArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="governance", name="read-audit-log", version="1.0.0"),
        display_name="Read Audit Log",
        description="Read the immutable governance audit log. Returns most recent entries.",
        read_scopes=["audit_logs"],
        write_scopes=[],
        side_effect_level="read",
        idempotent=True,
    )
    args_model = ReadAuditLogArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        logs = view.get_collection("audit_logs") if view.has_scope("audit_logs") else {}
        entries = list(logs.values()) if isinstance(logs, dict) else logs if isinstance(logs, list) else []
        if args.actor_filter:
            entries = [e for e in entries if isinstance(e, dict) and e.get("actor_id") == args.actor_filter]
        return {"audit_entries": entries[-args.limit:], "total": len(entries)}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
