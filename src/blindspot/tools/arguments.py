"""Argument validation and JSON schema generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from blindspot.tools.errors import ToolError


def validate_arguments(
    model_cls: type[BaseModel],
    raw: dict[str, Any],
) -> tuple[BaseModel | None, ToolError | None]:
    """Parse raw dict into model_cls; return (instance, None) or (None, error)."""
    try:
        return model_cls(**raw), None
    except ValidationError as exc:
        msgs = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        )
        return None, ToolError.validation(f"Argument validation failed: {msgs}")
    except Exception as exc:
        return None, ToolError.validation(str(exc))


def pydantic_to_tool_schema(
    model: type[BaseModel],
    *,
    name: str,
    description: str,
) -> dict[str, Any]:
    """Generate a function-calling compatible JSON schema from a Pydantic model."""
    schema = model.model_json_schema()
    return {
        "name": name,
        "description": description,
        "parameters": schema,
    }
