"""Artifact integrity checks — checksums, schema, completeness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from blindspot.verification.findings import VerificationFinding, _finding


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_integrity(run_dir: Path, config: Any) -> tuple[bool, list[VerificationFinding]]:
    """Check all required artifacts exist and checksums match."""
    findings: list[VerificationFinding] = []
    required_files = ["run_manifest.json", "trajectory.jsonl", "final_state.json"]

    for fname in required_files:
        p = run_dir / fname
        if not p.exists():
            findings.append(_finding(
                "integrity.missing_artifact", "fail", "error",
                details={"file": fname},
            ))

    if findings:
        return False, findings

    # Validate manifest is parseable
    try:
        manifest = json.loads((run_dir / "run_manifest.json").read_text())
    except Exception as exc:
        findings.append(_finding(
            "integrity.manifest_unparseable", "fail", "error",
            details={"error": str(exc)},
        ))
        return False, findings

    # Validate trajectory JSONL
    traj_path = run_dir / "trajectory.jsonl"
    steps: list[dict[str, Any]] = []
    try:
        for line in traj_path.read_text().splitlines():
            if line.strip():
                steps.append(json.loads(line))
    except Exception as exc:
        findings.append(_finding(
            "integrity.trajectory_unparseable", "fail", "error",
            details={"error": str(exc)},
        ))
        return False, findings

    # Check monotonic steps
    step_nums = [s.get("step", 0) for s in steps]
    for i in range(1, len(step_nums)):
        if step_nums[i] < step_nums[i - 1]:
            findings.append(_finding(
                "integrity.nonmonotonic_steps", "fail", "error",
                details={"step_i": i, "step_val": step_nums[i], "prev": step_nums[i-1]},
            ))
            return False, findings

    # Check checksums if manifest contains them
    stored_checksums = manifest.get("artifact_checksums", {})
    if stored_checksums.get("trajectory"):
        actual = hashlib.sha256(traj_path.read_bytes()).hexdigest()[:16]
        expected = stored_checksums["trajectory"]
        if actual != expected and config.reject_on_checksum_failure:
            findings.append(_finding(
                "integrity.checksum_mismatch", "fail", "error",
                details={"file": "trajectory.jsonl", "expected": expected, "actual": actual},
            ))
            return False, findings

    findings.append(_finding("integrity.all_checks", "pass", "info"))
    return True, findings
