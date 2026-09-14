"""list-accounts tool."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class ListAccountsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ListAccountsTool(PythonTool[ListAccountsArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="finance", name="list-accounts", version="1.0.0"),
        display_name="List Accounts",
        description="List financial accounts visible to the actor.",
        read_scopes=["accounts", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = ListAccountsArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: ListAccountsArgs, context: ToolExecutionContext) -> Any:
        accounts = view.get_collection("accounts") if view.has_scope("accounts") else {}
        result = []
        for aid, a in accounts.items():
            if not isinstance(a, dict):
                continue
            # Mask balance for non-owners
            masked = {
                "account_id": aid,
                "account_type": a.get("account_type"),
                "owner_id": a.get("owner_id"),
                "currency": a.get("currency", "USD"),
            }
            if a.get("owner_id") == context.actor_id or context.actor_id in a.get("authorized_users", []):
                masked["balance_usd"] = a.get("balance_usd")
            result.append(masked)
        return {"accounts": result}

    def plan_mutations(self, view: ReadOnlyStateView, args: ListAccountsArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
