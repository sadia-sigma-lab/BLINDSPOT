"""create-ticket tool for customer service domain."""
from __future__ import annotations
import uuid
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView

_VALID_PRIORITIES = frozenset({"low", "medium", "high", "urgent"})


class CreateTicketArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str
    subject: str
    description: str
    priority: str = "medium"


class CreateTicketTool(PythonTool[CreateTicketArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="create-ticket", version="1.0.0"),
        display_name="Create Support Ticket",
        description="Create a new support ticket for a customer.",
        read_scopes=["accounts", "resources"],
        write_scopes=["tickets", "resources"],
        side_effect_level="low",
    )
    args_model = CreateTicketArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: CreateTicketArgs, context: ToolExecutionContext) -> Any:
        if args.priority not in _VALID_PRIORITIES:
            raise ValueError(f"Invalid priority {args.priority!r}; must be one of {sorted(_VALID_PRIORITIES)}")
        ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
        return {
            "ticket_id": ticket_id,
            "customer_id": args.customer_id,
            "subject": args.subject,
            "status": "open",
            "priority": args.priority,
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: CreateTicketArgs, context: ToolExecutionContext) -> MutationPlan:
        if args.priority not in _VALID_PRIORITIES:
            return MutationPlan()
        ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"
        new_ticket = {
            "entity_id": ticket_id,
            "schema_version": "1.0.0",
            "resource_type": "ticket",
            "owner_id": args.customer_id,
            "organization_id": "org_acme",
            "classification": "internal",
            "customer_id": args.customer_id,
            "subject": args.subject,
            "description": args.description,
            "status": "open",
            "priority": args.priority,
            "assigned_to": None,
            "resolution": None,
            "tags": [],
            "attributes": {},
        }
        return MutationPlan(operations=[MutationOperation(
            collection="tickets",
            entity_id=ticket_id,
            operation="create",
            before=None,
            after=new_ticket,
            changed_fields=list(new_ticket.keys()),
        )])
