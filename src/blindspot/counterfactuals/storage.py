"""Counterfactual branch storage."""

from __future__ import annotations

import json
from pathlib import Path

from blindspot.counterfactuals.branching import BranchComparison, BranchResult


class BranchStore:
    """Stores branch results under data/counterfactuals/."""

    def __init__(self, counterfactuals_root: Path) -> None:
        self._root = counterfactuals_root

    def write(
        self,
        result: BranchResult,
        comparison: BranchComparison | None = None,
    ) -> Path:
        out_dir = self._root / result.branch_id
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "branch_manifest.json").write_text(
            json.dumps({
                "branch_id": result.branch_id,
                "source_verified_id": result.source_verified_id,
                "source_step": result.source_step,
                "intervention_id": result.intervention_id,
                "status": result.status,
                "goal_score": result.goal_score,
                "harm_score": result.harm_score,
                "created_at": str(result.created_at),
            }, indent=2),
            encoding="utf-8",
        )

        (out_dir / "lineage.json").write_text(
            json.dumps(result.lineage, indent=2, default=str), encoding="utf-8"
        )

        if comparison:
            (out_dir / "comparison.json").write_text(
                json.dumps(comparison.model_dump(), indent=2), encoding="utf-8"
            )

        return out_dir
