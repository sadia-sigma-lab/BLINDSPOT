"""Directory adapter — treats a directory tree as a structured collection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from blindspot.data_adapters.base import DataAdapter


def _file_checksum(path: Path) -> str:
    """Compute SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DirectoryManifestEntry(BaseModel):
    """Metadata for one file within a directory collection."""

    relative_path: str
    checksum: str
    size_bytes: int
    visibility: str = "private"


class DirectoryAdapter(DataAdapter):
    """Read a directory tree and produce a manifest of its files."""

    format_name = "directory"

    def load(self, path: Path, schema: Type[BaseModel] | None = None) -> list[DirectoryManifestEntry]:
        if not path.is_dir():
            raise ValueError(f"Expected a directory at {path}")
        entries: list[DirectoryManifestEntry] = []
        for child in sorted(path.rglob("*")):
            if child.is_file():
                rel = child.relative_to(path)
                entries.append(
                    DirectoryManifestEntry(
                        relative_path=str(rel),
                        checksum=_file_checksum(child),
                        size_bytes=child.stat().st_size,
                    )
                )
        return entries

    def dump(self, path: Path, data: Any) -> None:
        """Write a manifest JSON alongside the directory."""
        path.parent.mkdir(parents=True, exist_ok=True)
        entries = self.load(path)
        manifest_path = path.parent / f"{path.name}.manifest.json"
        manifest_path.write_text(
            json.dumps([e.model_dump() for e in entries], indent=2),
            encoding="utf-8",
        )

    def validate(self, path: Path, schema: Type[BaseModel] | None = None) -> None:
        if not path.is_dir():
            raise ValueError(f"Expected a directory at {path}")
