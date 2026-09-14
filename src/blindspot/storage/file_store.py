"""Filesystem-backed artifact store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from blindspot.exceptions import PathTraversalError
from blindspot.storage.artifact_store import ArtifactStore


class FileStore(ArtifactStore):
    """Stores all artifacts as files under a configured root directory."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def _safe_path(self, relative_path: str) -> Path:
        """Resolve relative_path and raise if it escapes the root."""
        resolved = (self._root / relative_path).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError as exc:
            raise PathTraversalError(
                f"Path {relative_path!r} escapes storage root {self._root}"
            ) from exc
        return resolved

    def write_json(self, relative_path: str, data: dict[str, Any]) -> str:
        path = self._safe_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return str(path)

    def write_jsonl(self, relative_path: str, records: Iterable[dict[str, Any]]) -> str:
        path = self._safe_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, default=str) + "\n")
        return str(path)

    def read_json(self, relative_path: str) -> dict[str, Any]:
        path = self._safe_path(relative_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return data  # type: ignore[return-value]

    def exists(self, relative_path: str) -> bool:
        try:
            return self._safe_path(relative_path).exists()
        except PathTraversalError:
            return False
