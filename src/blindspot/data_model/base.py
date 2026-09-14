"""Base entity model shared by all domain records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseEntity(BaseModel):
    """Root model for all versioned, identifiable domain entities."""

    model_config = ConfigDict(frozen=True)

    entity_id: str
    schema_version: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("created_at", "updated_at")
    @classmethod
    def _require_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("Timestamps must be timezone-aware")
        return v

    @field_validator("entity_id")
    @classmethod
    def _non_empty_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("entity_id must not be empty")
        return v

    @field_validator("schema_version")
    @classmethod
    def _non_empty_version(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("schema_version must not be empty")
        return v
