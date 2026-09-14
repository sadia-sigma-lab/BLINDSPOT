"""Scenario parameter utilities — deterministic ID generation."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_scenario_id(template_id: str, params: dict[str, Any], seed: int) -> str:
    """Generate a stable, deterministic scenario ID."""
    key = json.dumps({"t": template_id, "p": params, "s": seed}, sort_keys=True)
    return f"gen-{hashlib.sha256(key.encode()).hexdigest()[:12]}"


def stable_resource_id(namespace: str, *parts: str) -> str:
    key = ":".join([namespace] + list(parts))
    return f"{namespace}_{hashlib.sha256(key.encode()).hexdigest()[:8]}"
