"""Batch simulation runner."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.simulation.manifests import RunManifest
from blindspot.simulation.orchestrator import EpisodeOrchestrator, RunConfig, RunResult


class BatchRunConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    batch_id: str
    run_configs: list[RunConfig]
    max_concurrency: int = 1
    fail_fast: bool = False
    resume_existing: bool = True
    retry_failed_runs: int = 0


class BatchResult(BaseModel):
    model_config = ConfigDict(frozen=False)

    batch_id: str
    total_runs: int
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    run_results: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "completed"


class BatchRunner:
    """Runs multiple episodes sequentially (or bounded-concurrency future extension)."""

    def __init__(self, orchestrator: EpisodeOrchestrator) -> None:
        self._orchestrator = orchestrator

    def run(self, config: BatchRunConfig) -> BatchResult:
        result = BatchResult(
            batch_id=config.batch_id,
            total_runs=len(config.run_configs),
        )

        for run_cfg in config.run_configs:
            try:
                run_result = self._orchestrator.run(run_cfg)
                result.run_results.append({
                    "run_id": run_result.run_id,
                    "status": run_result.status,
                    "scenario_id": run_result.scenario_id,
                    "total_steps": run_result.total_steps,
                })
                result.completed += 1
            except Exception as exc:
                result.failed += 1
                result.run_results.append({
                    "run_id": run_cfg.run_id or "unknown",
                    "status": "failed",
                    "error": str(exc),
                })
                if config.fail_fast:
                    result.status = "failed"
                    break

        return result
