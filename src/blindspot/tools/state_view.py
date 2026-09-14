"""Read-only scoped state view."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from blindspot.core.state import WorldState
from blindspot.tools.errors import ToolError

# Collections that are never accessible through a state view regardless of scopes
_ALWAYS_HIDDEN = frozenset({"hidden", "grading", "attack_state", "__hidden__"})


class ScopeViolationError(Exception):
    """Raised when a tool accesses a collection outside its declared scopes."""
    def __init__(self, collection: str) -> None:
        super().__init__(f"Scope violation: tool has no read access to {collection!r}")
        self.collection = collection


class ReadOnlyStateView:
    """Provides scoped, immutable access to WorldState collections."""

    def __init__(self, state: WorldState, read_scopes: frozenset[str]) -> None:
        self._state = state
        self._read_scopes = read_scopes

    def get_collection(self, name: str) -> Mapping[str, Any]:
        """Return a read-only copy of the named collection."""
        if name in _ALWAYS_HIDDEN:
            raise ScopeViolationError(name)
        if name not in self._read_scopes:
            raise ScopeViolationError(name)
        value = self._state.public.get(name, {})
        return copy.deepcopy(value)

    def get_entity(self, collection: str, entity_id: str) -> Any:
        """Return a single entity from a collection."""
        coll = self.get_collection(collection)
        entity = coll.get(entity_id)
        return entity

    def has_scope(self, name: str) -> bool:
        return name in self._read_scopes and name not in _ALWAYS_HIDDEN

    def validate_write_scopes(self, planned_collections: list[str], allowed: list[str]) -> ToolError | None:
        """Return an error if any planned write targets a collection outside allowed scopes."""
        allowed_set = frozenset(allowed)
        for coll in planned_collections:
            if coll in _ALWAYS_HIDDEN:
                return ToolError.scope_violation(coll)
            if coll not in allowed_set:
                return ToolError.scope_violation(coll)
        return None
