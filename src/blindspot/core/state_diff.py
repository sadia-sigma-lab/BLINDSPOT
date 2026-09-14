"""State diff contract and application logic."""

import copy
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from blindspot.exceptions import StateError


class StateMutation(BaseModel):
    """A single field-level mutation within a state transition."""

    model_config = ConfigDict(frozen=True)

    path: str
    operation: Literal["add", "replace", "remove"]
    before: Any | None = None
    after: Any | None = None


class StateDiff(BaseModel):
    """Structured record of all mutations produced by one tool execution."""

    model_config = ConfigDict(frozen=True)

    mutations: list[StateMutation]
    emitted_event_ids: list[str] = []

    @property
    def is_empty(self) -> bool:
        return len(self.mutations) == 0

    def inverse(self) -> "StateDiff":
        """Return the inverse diff (swap before/after for undo support)."""
        inverse_mutations: list[StateMutation] = []
        for m in reversed(self.mutations):
            if m.operation == "add":
                inv_op: Literal["add", "replace", "remove"] = "remove"
                inverse_mutations.append(
                    StateMutation(path=m.path, operation=inv_op, before=m.after, after=m.before)
                )
            elif m.operation == "remove":
                inv_op = "add"
                inverse_mutations.append(
                    StateMutation(path=m.path, operation=inv_op, before=m.after, after=m.before)
                )
            else:
                inverse_mutations.append(
                    StateMutation(
                        path=m.path, operation="replace", before=m.after, after=m.before
                    )
                )
        return StateDiff(mutations=inverse_mutations)


def _resolve_path(obj: dict[str, Any], path: str) -> tuple[Any, str]:
    """Return (parent_container, final_key) for a dot-separated path."""
    parts = path.split(".")
    current: Any = obj
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise StateError(f"Path segment {part!r} not found in state for path {path!r}")
        current = current[part]
    return current, parts[-1]


def apply_diff(state_dict: dict[str, Any], diff: StateDiff) -> dict[str, Any]:
    """Apply a StateDiff to a raw state dictionary in place; return it."""
    result = copy.deepcopy(state_dict)
    for mutation in diff.mutations:
        try:
            parent, key = _resolve_path(result, mutation.path)
        except StateError:
            if mutation.operation == "add":
                # create intermediate dicts
                parts = mutation.path.split(".")
                node: Any = result
                for part in parts[:-1]:
                    node = node.setdefault(part, {})
                parent, key = node, parts[-1]
            else:
                raise
        if mutation.operation == "add":
            parent[key] = copy.deepcopy(mutation.after)
        elif mutation.operation == "replace":
            parent[key] = copy.deepcopy(mutation.after)
        elif mutation.operation == "remove":
            if isinstance(parent, dict):
                parent.pop(key, None)
    return result
