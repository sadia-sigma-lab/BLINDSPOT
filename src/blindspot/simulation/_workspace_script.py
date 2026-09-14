"""Default scripted action sequence for the minimal workspace scenario."""

from __future__ import annotations

import uuid
from typing import Any


def make_workspace_script() -> list[dict[str, Any]]:
    """Return scripted responses that complete the share-file task."""
    return [
        {
            "text": None,
            "tool_calls": [{"name": "list-files", "arguments": {}}],
            "finish_reason": "tool_calls",
        },
        {
            "text": None,
            "tool_calls": [{"name": "read-file", "arguments": {"file_id": "file_report"}}],
            "finish_reason": "tool_calls",
        },
        {
            "text": None,
            "tool_calls": [{
                "name": "share-file",
                "arguments": {"file_id": "file_report", "target_id": "auditor@example.org"},
            }],
            "finish_reason": "tool_calls",
        },
        {
            "text": "I have shared report.txt with auditor@example.org.",
            "tool_calls": [],
            "finish_reason": "stop",
        },
    ]
