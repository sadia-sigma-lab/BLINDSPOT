"""Organization record model."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class OrganizationRecord(BaseEntity):
    """Represents a tenant, department, or organizational unit."""

    model_config = ConfigDict(frozen=True)

    name: str
    tenant_id: str
    parent_organization_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
