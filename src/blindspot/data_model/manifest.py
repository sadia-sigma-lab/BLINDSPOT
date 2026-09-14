"""Fixture manifest schema and loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from blindspot.exceptions import ConfigurationError


class FixtureFileEntry(BaseModel):
    """Describes one data file within a fixture bundle."""

    model_config = ConfigDict(frozen=True)

    path: str
    format: Literal["json", "jsonl", "csv", "parquet", "markdown", "directory"]
    collection: str
    schema_ref: str | None = Field(None, alias="schema")
    visibility: Literal["public", "private", "hidden"]
    checksum: str | None = None

    model_config = ConfigDict(frozen=True, populate_by_name=True)


class FixtureRelationship(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_: str = Field(alias="from")
    to_any_of: list[str]

    model_config = ConfigDict(frozen=True, populate_by_name=True)


class FixtureProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    created_by: str
    created_at: str
    source: str
    license: str


class FixtureManifest(BaseModel):
    """Root manifest for a fixture bundle."""

    model_config = ConfigDict(frozen=True)

    fixture_id: str
    domain_id: str
    schema_version: str
    fixture_version: str
    seed: int
    files: list[FixtureFileEntry]
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    invariants: list[str] = Field(default_factory=list)
    provenance: FixtureProvenance | None = None

    @field_validator("files")
    @classmethod
    def _no_duplicate_collections(cls, v: list[FixtureFileEntry]) -> list[FixtureFileEntry]:
        collections = [f.collection for f in v]
        seen: set[str] = set()
        for c in collections:
            if c in seen:
                raise ValueError(f"Duplicate collection in manifest: {c!r}")
            seen.add(c)
        return v

    def hidden_files(self) -> list[FixtureFileEntry]:
        return [f for f in self.files if f.visibility == "hidden"]

    def visible_files(self) -> list[FixtureFileEntry]:
        return [f for f in self.files if f.visibility != "hidden"]


def load_manifest(manifest_path: Path) -> FixtureManifest:
    """Load and validate a fixture manifest YAML file."""
    if not manifest_path.exists():
        raise ConfigurationError(f"Manifest not found: {manifest_path}")
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Malformed manifest YAML: {exc}") from exc
    try:
        return FixtureManifest(**raw)
    except Exception as exc:
        raise ConfigurationError(f"Invalid manifest at {manifest_path}: {exc}") from exc
