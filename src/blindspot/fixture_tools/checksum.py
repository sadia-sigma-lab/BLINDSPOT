"""Checksum utilities for fixture files."""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_checksum(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_bundle_checksums(fixture_dir: Path) -> dict[str, str]:
    """Compute checksums for all files in a fixture directory tree."""
    result: dict[str, str] = {}
    for path in sorted(fixture_dir.rglob("*")):
        if path.is_file() and path.name != "manifest.yaml":
            rel = str(path.relative_to(fixture_dir))
            result[rel] = file_checksum(path)
    return result
