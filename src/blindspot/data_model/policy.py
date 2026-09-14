"""Policy rule and document models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from blindspot.data_model.base import BaseEntity


class PolicyRule(BaseModel):
    """A single evaluatable policy rule."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    description: str
    effect: Literal["allow", "deny", "require_approval", "require_verification"]
    action_pattern: str
    subject_conditions: dict[str, Any] = Field(default_factory=dict)
    resource_conditions: dict[str, Any] = Field(default_factory=dict)
    context_conditions: dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    enabled: bool = True

    @field_validator("rule_id")
    @classmethod
    def _non_empty_rule_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("rule_id must not be empty")
        return v


class PolicyDocument(BaseEntity):
    """A versioned policy document containing one or more rules."""

    model_config = ConfigDict(frozen=True)

    title: str
    domain: str
    rules: list[PolicyRule]
    source_path: str | None = None
    human_readable_path: str | None = None

    @field_validator("rules")
    @classmethod
    def _unique_rule_ids(cls, v: list[PolicyRule]) -> list[PolicyRule]:
        ids = [r.rule_id for r in v]
        if len(ids) != len(set(ids)):
            raise ValueError("PolicyDocument must have unique rule_ids")
        return v
