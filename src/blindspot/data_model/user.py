"""User record model."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class UserRecord(BaseEntity):
    """Represents an agent, human, or system actor within a domain."""

    model_config = ConfigDict(frozen=True)

    name: str
    email: str | None = None
    organization_id: str
    role_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
    clearance: str | None = None
    active: bool = True
    attributes: dict[str, Any] = Field(default_factory=dict)
