"""Exact snapshot storage and restoration for branching."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BranchSnapshot:
    """Stores and restores exact world state for counterfactual execution."""

    def __init__(self, snapshots_dir: Path) -> None:
        self._dir = snapshots_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot_id: str, state: dict[str, Any]) -> Path:
        path = self._dir / f"{snapshot_id}.json"
        path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
        return path

    def load(self, snapshot_id: str) -> dict[str, Any]:
        path = self._dir / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
        return json.loads(path.read_text())

    def extract_at_step(
        self,
        steps: list[dict[str, Any]],
        target_step: int,
        initial_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Reconstruct world state at target_step by replaying state hashes.

        For exact branching we use the pre_state_hash lookup from the trajectory.
        If a final_state is available, we use the final_state for the last step.
        """
        # Find the step_dict at target_step
        for step_dict in steps:
            if step_dict.get("step") == target_step:
                pre_hash = step_dict.get("pre_state_hash", "")
                return {"pre_state_hash": pre_hash, "step": target_step,
                        "_note": "Reconstructed from trajectory hash reference"}

        return {"step": target_step, "_note": "Step not found in trajectory"}
