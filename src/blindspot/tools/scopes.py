"""Scope declarations for tools."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StateScope(BaseModel):
    model_config = ConfigDict(frozen=True)
    collection: str
    fields: frozenset[str] | None = None


class ScopePolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    read_scopes: list[StateScope]
    write_scopes: list[StateScope]
