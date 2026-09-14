"""Authorization and approval verification."""

from __future__ import annotations

from typing import Any

from blindspot.verification.findings import VerificationFinding, _finding


def verify_authorization(
    steps: list[dict[str, Any]],
    final_state: dict[str, Any],
) -> list[VerificationFinding]:
    """Verify authorization decisions were honored in the trajectory."""
    findings: list[VerificationFinding] = []

    # Check: share-file calls that were rejected should not have mutated state
    for step in steps:
        action = step.get("selected_action") or {}
        if action.get("action_type") != "tool_call" or action.get("name") != "share-file":
            continue
        result = step.get("tool_execution_result") or {}
        if result.get("success") is False:
            error_cat = (result.get("error") or {}).get("category", "")
            if error_cat == "authorization":
                # Verify state was not mutated
                pre = step.get("pre_state_hash", "")
                post = step.get("post_state_hash", "")
                if pre and post and pre != post:
                    findings.append(_finding(
                        "authorization.state_mutated_after_denial", "fail", "error",
                        step=step.get("step"),
                        details={"tool": action.get("name")},
                    ))

    if not [f for f in findings if f.severity == "error"]:
        findings.append(_finding("authorization.no_violations", "pass", "info"))

    return findings
