"""Attack registry — stores and retrieves Attack implementations."""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Any

from blindspot.attacks.exceptions import AttackNotFoundError, AttackRegistrationError

if TYPE_CHECKING:
    from blindspot.attacks.base import Attack
    from blindspot.attacks.metadata import AttackMetadata


class AttackRegistry:
    """Ordered registry of Attack implementations keyed by canonical ID."""

    def __init__(self, name: str = "attacks") -> None:
        self._name = name
        self._store: OrderedDict[str, "Attack"] = OrderedDict()
        self._aliases: dict[str, str] = {}

    def register(self, attack: "Attack") -> None:
        cid = attack.metadata.attack_id.canonical()
        if cid in self._store:
            raise AttackRegistrationError(f"Attack already registered: {cid!r}")
        if attack.metadata.deprecated:
            import warnings
            warnings.warn(f"Registering deprecated attack: {cid}", stacklevel=2)
        self._store[cid] = attack

    def register_alias(self, alias: str, canonical_id: str) -> None:
        if alias in self._aliases or alias in self._store:
            raise AttackRegistrationError(f"Alias already exists: {alias!r}")
        if canonical_id not in self._store:
            raise AttackNotFoundError(canonical_id)
        self._aliases[alias] = canonical_id

    def get(self, attack_id: str) -> "Attack":
        resolved = self._aliases.get(attack_id, attack_id)
        attack = self._store.get(resolved)
        if attack is None:
            raise AttackNotFoundError(attack_id)
        return attack

    def contains(self, attack_id: str) -> bool:
        resolved = self._aliases.get(attack_id, attack_id)
        return resolved in self._store

    def list(self) -> list[str]:
        return list(self._store.keys())

    def list_by_family(self, family: str) -> list[str]:
        return [cid for cid, a in self._store.items() if a.metadata.family == family]

    def unregister(self, attack_id: str) -> None:
        if attack_id not in self._store:
            raise AttackNotFoundError(attack_id)
        del self._store[attack_id]
        stale = [k for k, v in self._aliases.items() if v == attack_id]
        for k in stale:
            del self._aliases[k]

    def clear(self) -> None:
        self._store.clear()
        self._aliases.clear()

    def all_metadata(self) -> list["AttackMetadata"]:
        return [a.metadata for a in self._store.values()]
