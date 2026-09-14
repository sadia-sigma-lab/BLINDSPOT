"""Rollback manager — opaque token-based state restoration."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff, apply_diff
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.errors import ToolError
from blindspot.tools.transaction import TransactionResult, _hash_public


class RollbackEntry:
    def __init__(self, token: str, inverse_diff: StateDiff, tool_id: str, actor_id: str) -> None:
        self.token = token
        self.inverse_diff = inverse_diff
        self.tool_id = tool_id
        self.actor_id = actor_id
        self.used = False
        self.created_at = datetime.now(tz=timezone.utc)


class RollbackManager:
    """Stores inverse diffs and restores state on demand."""

    def __init__(self) -> None:
        self._entries: dict[str, RollbackEntry] = {}

    def create_token(
        self,
        transaction: TransactionResult,
        tool_id: str,
        actor_id: str,
    ) -> str:
        """Issue a one-time rollback token for the given transaction."""
        token = str(uuid.uuid4())
        inverse = transaction.state_diff.inverse()
        self._entries[token] = RollbackEntry(token, inverse, tool_id, actor_id)
        return token

    def rollback(
        self,
        state: WorldState,
        rollback_token: str,
        actor_id: str,
        context: ToolExecutionContext,
    ) -> tuple[WorldState, TransactionResult, ToolError | None]:
        """Apply the inverse diff; return new state, result, error."""
        entry = self._entries.get(rollback_token)
        if entry is None:
            return state, _empty_result(), ToolError.not_found("rollback token", rollback_token)
        if entry.used:
            return state, _empty_result(), ToolError.conflict("Rollback token already consumed")
        # Authorization: only original actor or admin can roll back
        if entry.actor_id != actor_id:
            return state, _empty_result(), ToolError.authorization("Only the original actor may roll back")

        entry.used = True
        pre_hash = _hash_public(state.public)

        state_dict = {
            "public": copy.deepcopy(state.public),
            "private": state.private,
            "hidden": state.hidden,
            "audit_log": state.audit_log,
        }
        new_dict = apply_diff(state_dict, entry.inverse_diff)

        new_state = WorldState(
            schema_version=state.schema_version,
            episode_id=state.episode_id,
            step=state.step,
            session_id=state.session_id,
            random_seed=state.random_seed,
            public=new_dict.get("public", state.public),
            private=new_dict.get("private", state.private),
            hidden=new_dict.get("hidden", state.hidden),
            audit_log=new_dict.get("audit_log", state.audit_log),
        )
        post_hash = _hash_public(new_state.public)

        from blindspot.validators.reports import ValidationReport
        result = TransactionResult(
            committed=True,
            state_diff=entry.inverse_diff,
            pre_state_hash=pre_hash,
            post_state_hash=post_hash,
            validation_report=ValidationReport(
                valid=True, issues=[], checked_files=0, checked_entities=0, fixture_id=""
            ),
        )
        return new_state, result, None


def _empty_result() -> TransactionResult:
    from blindspot.validators.reports import ValidationReport
    return TransactionResult(
        committed=False, pre_state_hash="", post_state_hash="",
        validation_report=ValidationReport(
            valid=False, issues=[], checked_files=0, checked_entities=0, fixture_id=""
        ),
    )
