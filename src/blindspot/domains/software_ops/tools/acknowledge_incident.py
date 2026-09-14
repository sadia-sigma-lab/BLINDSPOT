"""acknowledge-incident tool."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification


class AcknowledgeIncidentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str
    note: str | None = None


class AcknowledgeIncidentTool(PythonTool[AcknowledgeIncidentArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="software-ops", name="acknowledge-incident", version="1.0.0"),
        display_name="Acknowledge Incident",
        description="Acknowledge an open incident and assign it to the actor.",
        read_scopes=["incidents", "resources"],
        write_scopes=["incidents", "resources"],
        required_permissions=["acknowledge"],
        side_effect_level="low",
    )
    args_model = AcknowledgeIncidentArgs
    output_model = BaseModel

    def read(self, view, args, context) -> Any:
        incidents = view.get_collection("incidents") if view.has_scope("incidents") else {}
        inc = incidents.get(args.incident_id, {})
        return {"incident_id": args.incident_id, "status": "acknowledged",
                "acknowledged_by": context.actor_id, "note": args.note}

    def plan_mutations(self, view, args, context) -> MutationPlan:
        incidents = view.get_collection("incidents") if view.has_scope("incidents") else {}
        inc = dict(incidents.get(args.incident_id, {}))
        if not inc:
            return MutationPlan()
        updated = {**inc, "status": "acknowledged",
                   "assigned_to": list(set(inc.get("assigned_to", []) + [context.actor_id]))}
        return MutationPlan(operations=[MutationOperation(
            collection="incidents", entity_id=args.incident_id,
            operation="update", before=inc, after=updated,
            changed_fields=["status", "assigned_to"],
        )])
