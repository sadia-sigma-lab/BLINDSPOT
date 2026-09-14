"""In-memory / file-backed memory store for agent episodic/semantic memory."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MemoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_id: str
    owner_actor_id: str
    memory_type: str  # episodic | semantic | preference | working
    content: str
    source_ids: list[str] = Field(default_factory=list)
    trust_level: str = "trusted"  # trusted | untrusted | unknown
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
    poisoned: bool = False  # verifier-only label


class MemoryStore:
    """File-backed memory store with BM25-compatible retrieval interface."""

    def __init__(self, persist_path: Path | None = None) -> None:
        self._entries: list[MemoryEntry] = []
        self._persist_path = persist_path
        if persist_path and persist_path.exists():
            self._load()

    def add(self, entry: MemoryEntry) -> str:
        self._entries.append(entry)
        if self._persist_path:
            self._save()
        return entry.entry_id

    def add_text(
        self,
        owner_actor_id: str,
        content: str,
        memory_type: str = "episodic",
        trust_level: str = "trusted",
        poisoned: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            owner_actor_id=owner_actor_id,
            memory_type=memory_type,
            content=content,
            trust_level=trust_level,
            poisoned=poisoned,
            metadata=metadata or {},
        )
        self.add(entry)
        return entry

    def retrieve(self, query: str, k: int = 5, actor_id: str | None = None) -> list[MemoryEntry]:
        """Return k most relevant entries via simple keyword overlap."""
        candidates = [
            e for e in self._entries
            if actor_id is None or e.owner_actor_id == actor_id
        ]
        if not candidates:
            return []

        query_tokens = set(query.lower().split())
        scored = []
        for entry in candidates:
            entry_tokens = set(entry.content.lower().split())
            overlap = len(query_tokens & entry_tokens)
            scored.append((overlap, entry))

        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored[:k]]

    def list_all(self, actor_id: str | None = None) -> list[MemoryEntry]:
        if actor_id:
            return [e for e in self._entries if e.owner_actor_id == actor_id]
        return list(self._entries)

    def list_poisoned(self) -> list[MemoryEntry]:
        return [e for e in self._entries if e.poisoned]

    def clear(self, actor_id: str | None = None) -> None:
        if actor_id:
            self._entries = [e for e in self._entries if e.owner_actor_id != actor_id]
        else:
            self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)

    def _save(self) -> None:
        if self._persist_path:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            data = [e.model_dump(mode="json") for e in self._entries]
            self._persist_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self._persist_path and self._persist_path.exists():
            data = json.loads(self._persist_path.read_text(encoding="utf-8"))
            self._entries = [MemoryEntry(**d) for d in data]
