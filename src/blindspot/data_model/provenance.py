"""Provenance record model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceRecord(BaseModel):
    """Tracks origin and lineage of data artifacts."""

    model_config = ConfigDict(frozen=True)

    provenance_id: str
    source_type: str
    source_id: str
    source_path: str | None = None
    generated_by: str | None = None
    parent_ids: list[str] = Field(default_factory=list)
    checksum: str | None = None
    notes: str | None = None
