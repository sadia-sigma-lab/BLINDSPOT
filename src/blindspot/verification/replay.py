"""Trajectory replay verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.verification.findings import VerificationFinding, _finding


class ReplayVerificationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    checked_steps: int = 0
    first_divergent_step: int | None = None
    expected_pre_hash: str | None = None
    actual_pre_hash: str | None = None
    expected_post_hash: str | None = None
    actual_post_hash: str | None = None
    event_order_match: bool = True
    attack_state_match: bool = True
    details: dict[str, Any] = Field(default_factory=dict)


def verify_replay(run_dir: Path, scenario_registry: Any | None = None) -> tuple[ReplayVerificationResult, list[VerificationFinding]]:
    """Verify state hash consistency across trajectory steps."""
    findings: list[VerificationFinding] = []
    traj_path = run_dir / "trajectory.jsonl"

    if not traj_path.exists():
        f = _finding("replay.missing_trajectory", "fail", "error")
        return ReplayVerificationResult(success=False), [f]

    steps: list[dict[str, Any]] = []
    for line in traj_path.read_text().splitlines():
        if line.strip():
            steps.append(json.loads(line))

    if not steps:
        f = _finding("replay.empty_trajectory", "fail", "error")
        return ReplayVerificationResult(success=False), [f]

    # Verify chaining: step[i].post_state_hash == step[i+1].pre_state_hash
    for i in range(len(steps) - 1):
        post = steps[i].get("post_state_hash", "")
        pre_next = steps[i + 1].get("pre_state_hash", "")
        if post and pre_next and post != pre_next:
            findings.append(_finding(
                "replay.hash_chain_break", "fail", "error",
                step=steps[i].get("step"),
                details={"post": post[:12], "pre_next": pre_next[:12]},
            ))
            return ReplayVerificationResult(
                success=False,
                checked_steps=i + 1,
                first_divergent_step=steps[i + 1].get("step"),
                expected_pre_hash=post,
                actual_pre_hash=pre_next,
            ), findings

    # Verify final state matches trajectory's last post hash
    final_hash_path = run_dir / "final_state_hash.txt"
    if final_hash_path.exists() and steps:
        stored_final = final_hash_path.read_text().strip()
        last_post = steps[-1].get("post_state_hash", "")
        if stored_final and last_post and stored_final != last_post:
            findings.append(_finding(
                "replay.final_hash_mismatch", "fail", "error",
                details={"stored": stored_final[:12], "trajectory": last_post[:12]},
            ))
            return ReplayVerificationResult(
                success=False, checked_steps=len(steps),
                expected_post_hash=stored_final, actual_post_hash=last_post,
            ), findings

    findings.append(_finding("replay.all_hashes_consistent", "pass", "info",
                              details={"steps_checked": len(steps)}))
    return ReplayVerificationResult(
        success=True, checked_steps=len(steps),
        event_order_match=True, attack_state_match=True,
    ), findings
