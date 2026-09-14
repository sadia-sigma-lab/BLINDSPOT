"""Trajectory reader for inspection and replay."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TrajectoryReader:
    def __init__(self, run_dir: Path) -> None:
        self._run_dir = run_dir

    def load_steps(self) -> list[dict[str, Any]]:
        path = self._run_dir / "trajectory.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    def load_manifest(self) -> dict[str, Any]:
        path = self._run_dir / "run_manifest.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text())

    def load_responses(self) -> list[dict[str, Any]]:
        path = self._run_dir / "provider_responses.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
