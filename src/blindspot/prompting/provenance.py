"""Prompt provenance — source hashes and template tracking."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_messages(messages: list[dict[str, Any]]) -> str:
    payload = json.dumps(messages, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def hash_tools(tools: list[dict[str, Any]]) -> str:
    payload = json.dumps(tools, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def compute_source_hashes(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    template_ids: list[str],
) -> dict[str, str]:
    return {
        "messages": hash_messages(messages),
        "tools": hash_tools(tools),
        "templates": hashlib.sha256(":".join(template_ids).encode()).hexdigest()[:16],
    }
