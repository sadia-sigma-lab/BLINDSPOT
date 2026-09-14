"""Domain-specific Pydantic schemas extending shared models."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from blindspot.data_model.resource import ResourceRecord


class WorkspaceFileRecord(ResourceRecord):
    """A file within the minimal workspace domain."""

    model_config = ConfigDict(frozen=True)

    name: str
    content: str = ""
    shared_with: list[str] = Field(default_factory=list)
    content_type: str = "text/plain"
    size_bytes: int = 0

    def is_shared_with(self, recipient: str) -> bool:
        return recipient in self.shared_with
