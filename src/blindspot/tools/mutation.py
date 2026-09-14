"""Mutation plan contracts."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.event import EnvironmentEvent


class MutationOperation(BaseModel):
    """A single staged change to one entity in one collection."""

    model_config = ConfigDict(frozen=True)

    collection: str
    entity_id: str
    operation: Literal["create", "update", "delete"]
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    changed_fields: list[str] = Field(default_factory=list)


class MutationPlan(BaseModel):
    """All planned mutations plus events for one tool execution."""

    model_config = ConfigDict(frozen=True)

    operations: list[MutationOperation] = Field(default_factory=list)
    events: list[EnvironmentEvent] = Field(default_factory=list)
    audit_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.operations and not self.events

    def affected_collections(self) -> list[str]:
        return list({op.collection for op in self.operations})
