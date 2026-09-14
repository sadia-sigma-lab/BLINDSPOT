"""Attack progress and success verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from blindspot.verification.findings import VerificationFinding, _finding


def verify_attacks(
    run_dir: Path,
    steps: list[dict[str, Any]],
    final_state: dict[str, Any],
    scenario: Any | None = None,
) -> list[VerificationFinding]:
    """Verify attack activation, progress, and success from trace files."""
    findings: list[VerificationFinding] = []
    trace_dir = run_dir / "attack_traces"

    if not trace_dir.exists():
        findings.append(_finding("attack.no_traces_dir", "pass", "info",
                                  details={"message": "No attack traces (clean scenario)"}))
        return findings

    trace_files = list(trace_dir.glob("*.jsonl"))
    if not trace_files:
        findings.append(_finding("attack.no_trace_files", "pass", "info"))
        return findings

    for trace_file in trace_files:
        attack_id = trace_file.stem.replace("attack_trace_", "").replace("_", ":")
        try:
            trace_steps = [json.loads(l) for l in trace_file.read_text().splitlines() if l.strip()]
        except Exception as exc:
            findings.append(_finding(
                "attack.trace_unparseable", "fail", "warning",
                details={"file": str(trace_file), "error": str(exc)},
            ))
            continue

        if trace_steps:
            findings.append(_finding(
                "attack.trace_present", "pass", "info",
                details={"attack_id": attack_id, "trace_steps": len(trace_steps)},
            ))

    return findings
