"""Tool call verification."""

from __future__ import annotations

import json
from typing import Any

from blindspot.verification.findings import VerificationFinding, _finding


def verify_tool_calls(
    steps: list[dict[str, Any]],
    enabled_tools: set[str],
) -> list[VerificationFinding]:
    """Verify all tool calls were registered, enabled, and have audit entries."""
    findings: list[VerificationFinding] = []

    for step in steps:
        action = step.get("selected_action") or {}
        if action.get("action_type") != "tool_call":
            continue

        tool_name = action.get("name", "")
        step_num = step.get("step", 0)

        if not tool_name:
            findings.append(_finding(
                "tool_call.missing_tool_name", "fail", "warning",
                step=step_num, details={"action": action},
            ))
            continue

        if tool_name not in enabled_tools:
            findings.append(_finding(
                "tool_call.unknown_tool", "fail", "error",
                step=step_num, details={"tool": tool_name, "enabled": sorted(enabled_tools)},
            ))
            continue

        # Check tool result was recorded
        result = step.get("tool_execution_result")
        if result is None:
            findings.append(_finding(
                "tool_call.missing_result", "fail", "warning",
                step=step_num, details={"tool": tool_name},
            ))

    if not [f for f in findings if f.severity == "error"]:
        findings.append(_finding("tool_calls.all_valid", "pass", "info"))

    return findings
