"""Approval record model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class ApprovalRecord(BaseEntity):
    """An approval or request record for a privileged action."""

    model_config = ConfigDict(frozen=True)

    requester_id: str
    approver_id: str
    action: str
    resource_id: str | None = None
    target_id: str | None = None
    scope: dict[str, Any] = Field(default_factory=dict)
    status: Literal["pending", "approved", "rejected", "expired", "revoked"]
    valid_until: datetime | None = None
    evidence: list[str] = Field(default_factory=list)

    def is_valid_at(self, t: datetime) -> bool:
        """Return True if the approval is approved and not expired."""
        if self.status != "approved":
            return False
        if self.valid_until and t >= self.valid_until:
            return False
        return True

    def covers(self, action: str, resource_id: str | None, target_id: str | None) -> bool:
        """Return True if this approval covers the given action and target."""
        if self.action != action:
            return False
        if self.resource_id is not None and self.resource_id != resource_id:
            return False
        if self.target_id is not None and self.target_id != target_id:
            return False
        return True
