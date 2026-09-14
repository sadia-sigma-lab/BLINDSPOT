"""Risk-labeled trajectory model and storage."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.risk.labels import StepRiskLabel
from blindspot.risk.point_of_no_return import PointOfNoReturnResult
from blindspot.risk.recoverability import RecoverabilityResult


class RiskLabeledTrajectory(BaseModel):
    model_config = ConfigDict(frozen=True)

    risk_labeled_id: str
    verified_id: str
    config_id: str
    step_labels: list[StepRiskLabel]
    point_of_no_return: PointOfNoReturnResult
    recoverability: list[RecoverabilityResult]
    branch_ids: list[str] = Field(default_factory=list)
    preference_pair_ids: list[str] = Field(default_factory=list)
    lineage: dict[str, Any] = Field(default_factory=dict)
    quality: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RiskLabeledWriter:
    """Writes risk-labeled trajectories under data/risk_labeled/."""

    def __init__(self, risk_root: Path) -> None:
        self._root = risk_root

    def write(self, rlt: RiskLabeledTrajectory) -> Path:
        out_dir = self._root / rlt.risk_labeled_id
        out_dir.mkdir(parents=True, exist_ok=True)

        # Step labels
        labels_path = out_dir / "step_labels.jsonl"
        with labels_path.open("w", encoding="utf-8") as f:
            for label in rlt.step_labels:
                f.write(json.dumps(label.model_dump(), default=str) + "\n")

        # PONR
        (out_dir / "point_of_no_return.json").write_text(
            json.dumps(rlt.point_of_no_return.model_dump(), indent=2), encoding="utf-8"
        )

        # Recoverability
        recov_path = out_dir / "recoverability.jsonl"
        with recov_path.open("w", encoding="utf-8") as f:
            for r in rlt.recoverability:
                f.write(json.dumps(r.model_dump()) + "\n")

        # Lineage and quality
        (out_dir / "lineage.json").write_text(
            json.dumps(rlt.lineage, indent=2, default=str), encoding="utf-8"
        )
        (out_dir / "quality.json").write_text(
            json.dumps(rlt.quality, indent=2), encoding="utf-8"
        )

        # Manifest with checksums
        checksums = {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            for p in out_dir.iterdir() if p.is_file()
        }
        manifest = {
            "risk_labeled_id": rlt.risk_labeled_id,
            "verified_id": rlt.verified_id,
            "config_id": rlt.config_id,
            "step_count": len(rlt.step_labels),
            "branch_ids": rlt.branch_ids,
            "preference_pair_ids": rlt.preference_pair_ids,
            "created_at": str(rlt.created_at),
            "checksums": checksums,
        }
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

        return out_dir
