"""Tool error contracts and typed error codes."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ToolErrorCategory = Literal[
    "validation",
    "authorization",
    "approval",
    "not_found",
    "conflict",
    "scope",
    "transient",
    "permanent",
    "internal",
]


class ToolError(BaseModel):
    """Structured, agent-visible error from a tool execution."""

    model_config = ConfigDict(frozen=True)

    code: str
    category: ToolErrorCategory
    message: str
    retryable: bool
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def validation(cls, message: str, details: dict[str, Any] | None = None) -> "ToolError":
        return cls(code="VALIDATION_ERROR", category="validation", message=message,
                   retryable=False, details=details or {})

    @classmethod
    def authorization(cls, message: str = "Access denied") -> "ToolError":
        return cls(code="AUTHORIZATION_DENIED", category="authorization", message=message,
                   retryable=False)

    @classmethod
    def approval_required(cls, action: str) -> "ToolError":
        return cls(code="APPROVAL_REQUIRED", category="approval",
                   message=f"A valid approval is required for action {action!r}",
                   retryable=False, details={"required_action": action})

    @classmethod
    def not_found(cls, resource: str, entity_id: str) -> "ToolError":
        return cls(code="NOT_FOUND", category="not_found",
                   message=f"{resource} {entity_id!r} not found",
                   retryable=False)

    @classmethod
    def scope_violation(cls, collection: str) -> "ToolError":
        return cls(code="SCOPE_VIOLATION", category="scope",
                   message=f"Tool does not have access to collection {collection!r}",
                   retryable=False)

    @classmethod
    def conflict(cls, message: str) -> "ToolError":
        return cls(code="CONFLICT", category="conflict", message=message, retryable=False)

    @classmethod
    def transient(cls, message: str = "Transient error; retry") -> "ToolError":
        return cls(code="TRANSIENT_ERROR", category="transient", message=message, retryable=True)

    @classmethod
    def internal(cls, message: str = "Internal error") -> "ToolError":
        return cls(code="INTERNAL_ERROR", category="internal", message=message, retryable=False)
