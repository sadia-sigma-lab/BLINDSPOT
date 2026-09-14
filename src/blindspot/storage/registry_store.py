"""Persist and load registry snapshots."""

from __future__ import annotations

from typing import Any

from blindspot.storage.file_store import FileStore


class RegistryStore:
    """Stores a snapshot of registered component IDs for a run."""

    def __init__(self, file_store: FileStore) -> None:
        self._store = file_store

    def save_registry_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> str:
        path = f"registry/{run_id}_registry.json"
        return self._store.write_json(path, snapshot)

    def load_registry_snapshot(self, run_id: str) -> dict[str, Any]:
        path = f"registry/{run_id}_registry.json"
        return self._store.read_json(path)
