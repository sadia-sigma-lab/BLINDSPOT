"""lookup-account tool for customer service domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView

_SENSITIVE_FIELDS = frozenset({"phone"})


class LookupAccountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    account_id: str


class LookupAccountTool(PythonTool[LookupAccountArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="lookup-account", version="1.0.0"),
        display_name="Lookup Account",
        description="Look up a customer account record by account ID.",
        read_scopes=["accounts", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = LookupAccountArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: LookupAccountArgs, context: ToolExecutionContext) -> Any:
        accounts = view.get_collection("accounts") if view.has_scope("accounts") else {}
        account = accounts.get(args.account_id)
        if account is None:
            raise ValueError(f"Account {args.account_id!r} not found")
        if not isinstance(account, dict):
            raise ValueError(f"Account {args.account_id!r} has unexpected format")
        # Omit sensitive fields
        return {k: v for k, v in account.items() if k not in _SENSITIVE_FIELDS}

    def plan_mutations(self, view: ReadOnlyStateView, args: LookupAccountArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
