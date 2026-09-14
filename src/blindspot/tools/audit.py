"""Audit sink — every tool call is recorded here."""

from __future__ import annotations

import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from blindspot.data_model.audit import AuditRecord
from blindspot.tools.context import ToolExecutionContext


def _hash_args(args: dict[str, Any]) -> str:
    """One-way hash of arguments so sensitive values are not stored in plaintext."""
    return hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]


class AuditSink(ABC):
    """Abstract audit sink — receives records from the tool runtime."""

    @abstractmethod
    def append(self, record: AuditRecord) -> str:
        """Store the record; return the record's entity_id."""
        ...

    @abstractmethod
    def list_for_episode(self, episode_id: str) -> list[AuditRecord]:
        ...


class InMemoryAuditSink(AuditSink):
    """Simple in-memory audit sink for tests and single-run sessions."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(self, record: AuditRecord) -> str:
        self._records.append(record)
        return record.entity_id

    def list_for_episode(self, episode_id: str) -> list[AuditRecord]:
        return [r for r in self._records if r.metadata.get("episode_id") == episode_id]


def build_audit_record(
    ctx: ToolExecutionContext,
    tool_id: str,
    raw_args: dict[str, Any],
    target_ids: list[str],
    result: str,
    policy_decision: str | None,
    diff_hash: str | None,
    event_ids: list[str],
    error_code: str | None = None,
    rollback_ref: str | None = None,
    idempotent: bool = False,
) -> AuditRecord:
    now = datetime.now(tz=timezone.utc)
    return AuditRecord(
        entity_id=str(uuid.uuid4()),
        schema_version="1.0.0",
        created_at=now,
        updated_at=now,
        step=ctx.step,
        actor_id=ctx.actor_id,
        action=tool_id,
        target_ids=target_ids,
        result=result,  # type: ignore[arg-type]
        policy_decision=policy_decision,
        state_diff_hash=diff_hash,
        provenance_ids=event_ids,
        metadata={
            "episode_id": ctx.episode_id,
            "session_id": ctx.session_id,
            "tool_call_id": ctx.tool_call_id,
            "args_hash": _hash_args(raw_args),
            "error_code": error_code,
            "rollback_ref": rollback_ref,
            "idempotent_replay": idempotent,
        },
    )
