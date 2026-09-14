"""Resource record model."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, field_validator

from blindspot.data_model.base import BaseEntity

_VALID_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted", "secret"}


class ResourceRecord(BaseEntity):
    """Generic resource owned by a user within an organization."""

    model_config = ConfigDict(frozen=True)

    resource_type: str
    owner_id: str
    organization_id: str
    classification: str
    tags: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("classification")
    @classmethod
    def _valid_classification(cls, v: str) -> str:
        if v not in _VALID_CLASSIFICATIONS:
            raise ValueError(
                f"classification must be one of {_VALID_CLASSIFICATIONS}, got {v!r}"
            )
        return v
