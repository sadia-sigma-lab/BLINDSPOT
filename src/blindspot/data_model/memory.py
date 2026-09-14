"""Memory record model for agent episodic and semantic memory."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from blindspot.data_model.base import BaseEntity


class MemoryRecord(BaseEntity):
    """A single memory item owned by an actor."""

    model_config = ConfigDict(frozen=True)

    owner_actor_id: str
    memory_type: Literal["episodic", "semantic", "preference", "working", "summary"]
    content: str
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    trust_level: Literal["trusted", "untrusted", "unknown"] = "unknown"
    expires_at: datetime | None = None
    visibility: Literal["public", "private", "hidden"] = "private"
    session_origin: str | None = None
    embedding_ref: str | None = None

    @field_validator("confidence")
    @classmethod
    def _valid_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"confidence must be in [0, 1], got {v}")
        return v

    def is_expired_at(self, t: datetime) -> bool:
        if self.expires_at is None:
            return False
        return t >= self.expires_at
