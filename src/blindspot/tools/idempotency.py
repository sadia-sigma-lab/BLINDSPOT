"""Idempotency store — prevents duplicate side effects on retry."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict

from blindspot.tools.errors import ToolError


class IdempotencyRecord(BaseModel):
    """Stored result for an idempotency key."""

    model_config = ConfigDict(frozen=True)

    key: str
    actor_id: str
    tool_id: str
    arguments_hash: str
    result_snapshot: dict[str, Any]
    created_at: datetime


def _args_hash(args: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()


class IdempotencyStore:
    """In-memory idempotency store keyed by (key, actor_id, tool_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str], IdempotencyRecord] = {}

    def check(
        self,
        key: str,
        actor_id: str,
        tool_id: str,
        raw_args: dict[str, Any],
    ) -> tuple[IdempotencyRecord | None, ToolError | None]:
        """Return stored record or None; error if args mismatch."""
        store_key = (key, actor_id, tool_id)
        record = self._store.get(store_key)
        if record is None:
            return None, None
        current_hash = _args_hash(raw_args)
        if record.arguments_hash != current_hash:
            return None, ToolError.conflict(
                f"Idempotency key {key!r} was already used with different arguments"
            )
        return record, None

    def store(
        self,
        key: str,
        actor_id: str,
        tool_id: str,
        raw_args: dict[str, Any],
        result_snapshot: dict[str, Any],
    ) -> IdempotencyRecord:
        store_key = (key, actor_id, tool_id)
        record = IdempotencyRecord(
            key=key,
            actor_id=actor_id,
            tool_id=tool_id,
            arguments_hash=_args_hash(raw_args),
            result_snapshot=result_snapshot,
            created_at=datetime.now(tz=timezone.utc),
        )
        self._store[store_key] = record
        return record
