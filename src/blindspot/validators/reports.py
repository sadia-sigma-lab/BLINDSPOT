"""Validation result models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ValidationIssue(BaseModel):
    """A single validation finding."""

    model_config = ConfigDict(frozen=True)

    severity: Literal["error", "warning", "info"]
    code: str
    message: str
    collection: str | None = None
    entity_id: str | None = None
    path: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    """Aggregated result of running validators against a fixture bundle."""

    model_config = ConfigDict(frozen=True)

    valid: bool
    issues: list[ValidationIssue]
    checked_files: int
    checked_entities: int
    fixture_id: str

    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
