"""Lineage tracking for verified artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def build_lineage(
    raw_run_id: str,
    raw_run_dir: Path,
    verification_config_id: str,
    verifier_version: str = "0.1.0",
    judge_configs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    manifest_path = raw_run_dir / "run_manifest.json"
    manifest_hash = ""
    if manifest_path.exists():
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()[:16]

    return {
        "raw_run_id": raw_run_id,
        "raw_manifest_hash": manifest_hash,
        "verification_config_id": verification_config_id,
        "verifier_version": verifier_version,
        "judge_configs": judge_configs or [],
        "raw_artifacts_unchanged": True,
        "derived_from": f"data/raw/runs/{raw_run_id}",
    }
