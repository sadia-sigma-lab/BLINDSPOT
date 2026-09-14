"""Append-only trajectory writer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class TrajectoryWriter:
    """Writes trajectory steps, responses, and final state to the run directory."""

    def __init__(self, run_dir: Path) -> None:
        self._run_dir = run_dir
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._traj_path = run_dir / "trajectory.jsonl"
        self._response_path = run_dir / "provider_responses.jsonl"

    def append_step(self, step: dict[str, Any]) -> None:
        with self._traj_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(step, default=str) + "\n")

    def write_response(self, response: dict[str, Any]) -> None:
        with self._response_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(response, default=str) + "\n")

    def write_final_state(self, state: dict[str, Any], state_hash: str) -> None:
        (self._run_dir / "final_state.json").write_text(
            json.dumps(state, indent=2, default=str), encoding="utf-8"
        )
        (self._run_dir / "final_state_hash.txt").write_text(state_hash, encoding="utf-8")

    def trajectory_checksum(self) -> str:
        if not self._traj_path.exists():
            return ""
        return hashlib.sha256(self._traj_path.read_bytes()).hexdigest()[:16]
