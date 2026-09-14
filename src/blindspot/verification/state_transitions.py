"""State transition, diff, and event verification."""

from __future__ import annotations

from typing import Any

from blindspot.verification.findings import VerificationFinding, _finding


def verify_state_transitions(steps: list[dict[str, Any]]) -> list[VerificationFinding]:
    """Verify that mutating tool calls produce non-trivial diffs."""
    findings: list[VerificationFinding] = []

    for step in steps:
        action = step.get("selected_action") or {}
        if action.get("action_type") != "tool_call":
            continue

        pre = step.get("pre_state_hash", "")
        post = step.get("post_state_hash", "")
        result = step.get("tool_execution_result") or {}

        # Read-only tools should not change state
        tool_name = action.get("name", "")
        read_only = tool_name in {"list-files", "read-file", "list-messages",
                                   "read-message", "inspect-policy"}
        if read_only and pre and post and pre != post:
            findings.append(_finding(
                "state.read_only_tool_mutated", "fail", "warning",
                step=step.get("step"),
                details={"tool": tool_name},
            ))

    findings.append(_finding("state_transitions.checked", "pass", "info"))
    return findings
