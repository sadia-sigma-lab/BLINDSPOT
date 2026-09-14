"""Visibility policy and state projection."""

from __future__ import annotations

import copy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.state import WorldState


class VisibilityPolicy(BaseModel):
    """Defines what a specific actor can read and write."""

    model_config = ConfigDict(frozen=True)

    actor_id: str
    readable_collections: set[str]
    writable_collections: set[str]
    field_filters: dict[str, list[str]] = Field(default_factory=dict)
    hidden_collections: set[str] = Field(default_factory=set)


class StateProjector:
    """Projects a WorldState to only the fields visible to a given actor."""

    def project(
        self,
        state: WorldState,
        actor_id: str,
        policy: VisibilityPolicy,
    ) -> dict[str, Any]:
        """Return a deep-copy projection containing only actor-visible data."""
        result: dict[str, Any] = {}

        # Public state: filter collections
        public_projection: dict[str, Any] = {}
        for key, value in state.public.items():
            if key in policy.hidden_collections:
                continue
            if key not in policy.readable_collections:
                continue
            projected = self._apply_field_filter(copy.deepcopy(value), key, policy)
            public_projection[key] = projected
        result["public"] = public_projection

        # Private state: only include if actor is explicitly allowed
        if actor_id in policy.readable_collections or "__private__" in policy.readable_collections:
            result["private"] = copy.deepcopy(state.private)
        else:
            result["private"] = {}

        # Hidden state is NEVER included
        result["hidden"] = {}

        return result

    def _apply_field_filter(
        self,
        value: Any,
        collection: str,
        policy: VisibilityPolicy,
    ) -> Any:
        """Remove fields listed in policy.field_filters from every record in the collection."""
        filters = policy.field_filters.get(collection, [])
        if not filters:
            return value
        if isinstance(value, dict):
            # If the dict values look like records (their values are dicts themselves),
            # filter fields from each record rather than from the outer dict.
            if value and all(isinstance(v, dict) for v in value.values()):
                return {
                    k: {fk: fv for fk, fv in rec.items() if fk not in filters}
                    for k, rec in value.items()
                }
            return {k: v for k, v in value.items() if k not in filters}
        if isinstance(value, list):
            return [self._apply_field_filter(item, collection, policy) for item in value]
        return value
