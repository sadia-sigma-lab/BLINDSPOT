"""Tool specification contract."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from blindspot.core.identifiers import ComponentID


class ToolSpecification(BaseModel):
    """Declarative metadata for a benchmark tool."""

    model_config = ConfigDict(frozen=True)

    tool_id: ComponentID
    display_name: str
    description: str
    read_scopes: list[str]
    write_scopes: list[str]
    required_permissions: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    approval_action: str | None = None
    reversible: bool = False
    idempotent: bool = False
    side_effect_level: Literal["none", "read", "low", "medium", "high", "critical"]
    visibility: Literal["public", "restricted", "hidden"] = "public"
    tags: list[str] = Field(default_factory=list)
    deprecated: bool = False

    @model_validator(mode="after")
    def _validate_consistency(self) -> "ToolSpecification":
        if self.side_effect_level == "none" and self.write_scopes:
            raise ValueError(
                "Read-only tools (side_effect_level='none') must have empty write_scopes"
            )
        if self.requires_approval and not self.approval_action:
            raise ValueError(
                "Tools with requires_approval=True must declare approval_action"
            )
        return self
