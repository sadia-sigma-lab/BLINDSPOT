"""Scenario family manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ScenarioFamilyManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family_id: str
    domain_id: str
    template_ids: list[str] = Field(default_factory=list)
    scenario_ids: list[str] = Field(default_factory=list)
    generation_config: str | None = None
    split_config: str | None = None
    schema_version: str = "1.0.0"
    license: str = "Apache-2.0"
    author: str = "benchmark-team"
    checksum: str | None = None


def load_family_manifest(path: Path) -> ScenarioFamilyManifest:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ScenarioFamilyManifest(**raw)


def compute_manifest_checksum(manifest: ScenarioFamilyManifest) -> str:
    payload = json.dumps(manifest.model_dump(), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
