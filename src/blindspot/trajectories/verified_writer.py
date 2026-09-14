"""Verified trajectory writer — stores output separately, never overwrites raw."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from blindspot.trajectories.verified import VerifiedTrajectory


class VerifiedWriter:
    def __init__(self, verified_root: Path) -> None:
        self._root = verified_root

    def write(self, vt: VerifiedTrajectory) -> Path:
        out_dir = self._root / vt.verified_id
        out_dir.mkdir(parents=True, exist_ok=True)

        # Main verified trajectory
        vt_path = out_dir / "verified_trajectory.json"
        vt_path.write_text(
            json.dumps(vt.model_dump(), indent=2, default=str), encoding="utf-8"
        )

        # Findings
        findings_path = out_dir / "findings.jsonl"
        with findings_path.open("w") as f:
            for finding in vt.findings:
                f.write(json.dumps(finding.model_dump(), default=str) + "\n")

        # Evidence
        ev_path = out_dir / "evidence.jsonl"
        with ev_path.open("w") as f:
            for ev in vt.evidence_index:
                f.write(json.dumps(ev.model_dump(), default=str) + "\n")

        # Quality and confidence
        (out_dir / "quality.json").write_text(
            json.dumps(vt.quality.model_dump(), indent=2), encoding="utf-8"
        )
        (out_dir / "confidence.json").write_text(
            json.dumps(vt.confidence.model_dump(), indent=2), encoding="utf-8"
        )

        # Lineage
        (out_dir / "lineage.json").write_text(
            json.dumps(vt.lineage, indent=2, default=str), encoding="utf-8"
        )

        # Manifest
        checksums = {
            f.name: hashlib.sha256(f.read_bytes()).hexdigest()[:16]
            for f in out_dir.iterdir() if f.is_file()
        }
        manifest = {
            "verified_id": vt.verified_id,
            "raw_run_id": vt.raw_run_id,
            "status": vt.verification_status.value,
            "created_at": str(vt.created_at),
            "checksums": checksums,
        }
        (out_dir / "verified_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

        return out_dir
