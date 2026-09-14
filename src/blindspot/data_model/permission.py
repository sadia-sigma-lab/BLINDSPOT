"""Permission record model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field, model_validator

from blindspot.data_model.base import BaseEntity


class PermissionRecord(BaseEntity):
    """A granted permission binding a subject to a resource and action."""

    model_config = ConfigDict(frozen=True)

    subject_type: Literal["user", "group", "role", "agent"]
    subject_id: str
    resource_id: str
    permission: str
    granted_by: str
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    conditions: dict[str, Any] = Field(default_factory=dict)
    active: bool = True

    @model_validator(mode="after")
    def _valid_window(self) -> "PermissionRecord":
        if self.valid_from and self.valid_until:
            if self.valid_from >= self.valid_until:
                raise ValueError("valid_from must be before valid_until")
        return self

    def is_active_at(self, t: datetime) -> bool:
        """Return True if this permission is active at time t."""
        if not self.active:
            return False
        if self.valid_from and t < self.valid_from:
            return False
        if self.valid_until and t >= self.valid_until:
            return False
        return True
