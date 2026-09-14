"""Fixture builder for constructing and writing fixture bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from blindspot.fixture_tools.checksum import file_checksum


def stable_id(namespace: str, *parts: str) -> str:
    """Generate a deterministic ID from namespace and parts."""
    key = ":".join([namespace] + list(parts))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


class FixtureCollectionDef:
    def __init__(
        self,
        name: str,
        records: list[Any],
        format: str,
        visibility: Literal["public", "private", "hidden"],
        schema_path: str,
        file_name: str | None = None,
    ) -> None:
        self.name = name
        self.records = records
        self.format = format
        self.visibility = visibility
        self.schema_path = schema_path
        self.file_name = file_name or f"{name}.{format if format != 'jsonl' else 'jsonl'}"


class FixtureBuilder:
    """Constructs a fixture bundle from collection definitions."""

    def __init__(self, fixture_id: str, domain_id: str, seed: int = 42) -> None:
        self._fixture_id = fixture_id
        self._domain_id = domain_id
        self._seed = seed
        self._collections: list[FixtureCollectionDef] = []

    def add_collection(
        self,
        name: str,
        records: list[BaseModel],
        format: str = "json",
        visibility: Literal["public", "private", "hidden"] = "private",
        schema_path: str = "",
    ) -> None:
        self._collections.append(
            FixtureCollectionDef(name, records, format, visibility, schema_path)
        )

    def write(self, output_dir: Path) -> Path:
        """Write all collection files and a manifest.yaml to output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "hidden").mkdir(exist_ok=True)

        file_entries: list[dict[str, Any]] = []

        for coll in self._collections:
            relative_path = (
                f"hidden/{coll.file_name}"
                if coll.visibility == "hidden"
                else coll.file_name
            )
            full_path = output_dir / relative_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            serializable = [
                r.model_dump() if isinstance(r, BaseModel) else r for r in coll.records
            ]

            if coll.format == "jsonl":
                lines = [json.dumps(r, default=str) for r in serializable]
                full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            else:
                full_path.write_text(
                    json.dumps(serializable, indent=2, default=str), encoding="utf-8"
                )

            checksum = file_checksum(full_path)
            file_entries.append({
                "path": relative_path,
                "format": coll.format,
                "collection": coll.name,
                "schema": coll.schema_path or None,
                "visibility": coll.visibility,
                "checksum": checksum,
            })

        # Write manifest
        import yaml
        manifest: dict[str, Any] = {
            "fixture_id": self._fixture_id,
            "domain_id": self._domain_id,
            "schema_version": "1.0.0",
            "fixture_version": "1.0.0",
            "seed": self._seed,
            "files": file_entries,
            "relationships": [],
            "invariants": [],
            "provenance": {
                "created_by": "FixtureBuilder",
                "created_at": "2026-01-01T00:00:00Z",
                "source": "generated",
                "license": "Apache-2.0",
            },
        }
        manifest_path = output_dir / "manifest.yaml"
        manifest_path.write_text(
            yaml.dump(manifest, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        return manifest_path
