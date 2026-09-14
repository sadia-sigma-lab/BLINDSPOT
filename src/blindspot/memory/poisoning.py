"""Memory poison injector — phase 1 ingestion for memory poisoning attack."""

from __future__ import annotations

from typing import Any

from blindspot.memory.store import MemoryEntry, MemoryStore


class MemoryPoisonInjector:
    """Injects poisoned memory entries into a MemoryStore."""

    def inject(
        self,
        store: MemoryStore,
        poison_records: list[dict[str, Any]],
        actor_id: str = "user_alice",
    ) -> list[MemoryEntry]:
        """Phase 1: inject all poisoned records into the store.

        Args:
            store: the target memory store
            poison_records: list of dicts with content, memory_type, etc.
            actor_id: actor whose memory is being poisoned

        Returns:
            list of injected MemoryEntry objects
        """
        injected: list[MemoryEntry] = []
        for rec in poison_records:
            entry = store.add_text(
                owner_actor_id=rec.get("owner_actor_id", actor_id),
                content=rec["content"],
                memory_type=rec.get("memory_type", "semantic"),
                trust_level=rec.get("trust_level", "untrusted"),
                poisoned=True,
                metadata=rec.get("metadata", {}),
            )
            injected.append(entry)
        return injected

    def verify_injection(self, store: MemoryStore, query: str, k: int = 5) -> bool:
        """Phase 1 verification: confirm injected records are retrievable.

        Returns True if at least one poisoned record appears in top-k results.
        """
        results = store.retrieve(query, k=k)
        return any(r.poisoned for r in results)

    def exploitation_check(
        self,
        store: MemoryStore,
        query: str,
        k: int = 3,
    ) -> tuple[bool, list[MemoryEntry]]:
        """Phase 2 check: confirm a retrieval returns poisoned records.

        Returns (any_poisoned, poisoned_results).
        """
        results = store.retrieve(query, k=k)
        poisoned = [r for r in results if r.poisoned]
        return bool(poisoned), poisoned
