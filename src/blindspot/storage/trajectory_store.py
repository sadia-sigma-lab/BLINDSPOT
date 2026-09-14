"""Append-only trajectory storage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from blindspot.storage.file_store import FileStore


class TrajectoryStore:
    """Write-once, append-only trajectory log within a run directory."""

    def __init__(self, file_store: FileStore, run_id: str) -> None:
        self._store = file_store
        self._run_id = run_id
        self._relative = f"raw/runs/{run_id}/trajectory.jsonl"

    def append_step(self, step_record: dict[str, Any]) -> None:
        """Append one trajectory step. Raw logs are never overwritten."""
        self._store.write_jsonl(self._relative, [step_record])

    @property
    def relative_path(self) -> str:
        return self._relative
