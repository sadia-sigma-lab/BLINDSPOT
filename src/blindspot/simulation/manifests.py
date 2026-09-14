"""Run manifest contract and storage."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RunManifest(BaseModel):
    model_config = ConfigDict(frozen=False)

    run_id: str
    status: Literal[
        "initialized", "running", "completed", "terminated",
        "truncated", "failed", "interrupted",
    ] = "initialized"
    scenario_id: str
    scenario_version: str = "1.0.0"
    fixture_id: str = ""
    seed: int = 42
    target_agent: dict[str, Any] = Field(default_factory=dict)
    simulators: list[dict[str, Any]] = Field(default_factory=list)
    plugins: list[dict[str, Any]] = Field(default_factory=list)
    package_version: str = "0.1.0"
    git_commit: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    completed_at: datetime | None = None
    termination_reasons: list[str] = Field(default_factory=list)
    artifact_checksums: dict[str, str] = Field(default_factory=dict)
    reproducibility: dict[str, Any] = Field(default_factory=dict)
    total_steps: int = 0
    total_tool_calls: int = 0

    def finalize(self, status: str, reasons: list[str]) -> None:
        self.status = status  # type: ignore[assignment]
        self.termination_reasons = reasons
        self.completed_at = datetime.now(tz=timezone.utc)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "RunManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)
