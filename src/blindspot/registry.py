"""Generic component registry and RegistryHub."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from blindspot.exceptions import ComponentNotFoundError, DuplicateRegistrationError

T = TypeVar("T")


class ComponentRegistry(Generic[T]):
    """Thread-safe ordered registry for benchmark components."""

    def __init__(self, name: str = "") -> None:
        self._name = name
        self._store: OrderedDict[str, T] = OrderedDict()
        self._aliases: dict[str, str] = {}

    def register(self, component_id: str, component: T) -> None:
        """Register a component under its canonical ID."""
        if component_id in self._store:
            raise DuplicateRegistrationError(component_id)
        self._store[component_id] = component

    def register_alias(self, alias: str, canonical_id: str) -> None:
        """Register an alias that resolves to an existing component."""
        if alias in self._aliases or alias in self._store:
            raise DuplicateRegistrationError(alias)
        if canonical_id not in self._store:
            raise ComponentNotFoundError(canonical_id, self._name)
        self._aliases[alias] = canonical_id

    def unregister(self, component_id: str) -> None:
        """Remove a component and any aliases pointing to it."""
        if component_id not in self._store:
            raise ComponentNotFoundError(component_id, self._name)
        del self._store[component_id]
        stale = [k for k, v in self._aliases.items() if v == component_id]
        for k in stale:
            del self._aliases[k]

    def get(self, component_id: str) -> T:
        """Retrieve a component by ID or alias."""
        resolved = self._aliases.get(component_id, component_id)
        if resolved not in self._store:
            raise ComponentNotFoundError(component_id, self._name)
        return self._store[resolved]

    def list(self) -> list[str]:
        """Return canonical IDs in insertion order."""
        return list(self._store.keys())

    def contains(self, component_id: str) -> bool:
        """Return True if the ID (or an alias) is registered."""
        resolved = self._aliases.get(component_id, component_id)
        return resolved in self._store

    def clear(self) -> None:
        """Remove all components and aliases."""
        self._store.clear()
        self._aliases.clear()

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"ComponentRegistry(name={self._name!r}, count={len(self._store)})"


@dataclass
class RegistryHub:
    """Central collection of all domain-specific registries."""

    domains: ComponentRegistry[Any] = field(default_factory=lambda: ComponentRegistry("domains"))
    tools: ComponentRegistry[Any] = field(default_factory=lambda: ComponentRegistry("tools"))
    attacks: ComponentRegistry[Any] = field(default_factory=lambda: ComponentRegistry("attacks"))
    scenarios: ComponentRegistry[Any] = field(
        default_factory=lambda: ComponentRegistry("scenarios")
    )
    evaluators: ComponentRegistry[Any] = field(
        default_factory=lambda: ComponentRegistry("evaluators")
    )
    actors: ComponentRegistry[Any] = field(default_factory=lambda: ComponentRegistry("actors"))
    policies: ComponentRegistry[Any] = field(
        default_factory=lambda: ComponentRegistry("policies")
    )
    interventions: ComponentRegistry[Any] = field(
        default_factory=lambda: ComponentRegistry("interventions")
    )

    def clear_all(self) -> None:
        """Clear every registry (useful for test isolation)."""
        for reg in (
            self.domains,
            self.tools,
            self.attacks,
            self.scenarios,
            self.evaluators,
            self.actors,
            self.policies,
            self.interventions,
        ):
            reg.clear()
