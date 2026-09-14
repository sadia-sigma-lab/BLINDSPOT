"""Audit record model."""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class AuditRecord(BaseEntity):
    """An immutable audit log entry for one actor action."""

    model_config = ConfigDict(frozen=True)

    step: int
    actor_id: str
    action: str
    target_ids: list[str] = Field(default_factory=list)
    result: Literal["success", "failure", "partial"]
    policy_decision: str | None = None
    state_diff_hash: str | None = None
    provenance_ids: list[str] = Field(default_factory=list)
