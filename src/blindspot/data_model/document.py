"""Document record model (extends ResourceRecord)."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from blindspot.data_model.resource import ResourceRecord


class DocumentRecord(ResourceRecord):
    """A versioned document resource with content and provenance."""

    model_config = ConfigDict(frozen=True)

    title: str
    content_path: str
    mime_type: str
    checksum: str
    version: int = 1
    derived_from: list[str] = Field(default_factory=list)
