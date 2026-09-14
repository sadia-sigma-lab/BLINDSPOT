"""list-incidents tool."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification


class ListIncidentsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severity_filter: str | None = None
    status_filter: str | None = None


class ListIncidentsTool(PythonTool[ListIncidentsArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="software-ops", name="list-incidents", version="1.0.0"),
        display_name="List Incidents",
        description="List active and recent incidents.",
        read_scopes=["incidents", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListIncidentsArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        incidents = view.get_collection("incidents") if view.has_scope("incidents") else {}
        result = []
        for iid, inc in incidents.items():
            if not isinstance(inc, dict):
                continue
            if args.severity_filter and inc.get("severity") != args.severity_filter:
                continue
            if args.status_filter and inc.get("status") != args.status_filter:
                continue
            result.append({
                "incident_id": iid,
                "severity": inc.get("severity"),
                "title": inc.get("title"),
                "status": inc.get("status"),
                "assigned_to": inc.get("assigned_to", []),
            })
        return {"incidents": result}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        return MutationPlan()
