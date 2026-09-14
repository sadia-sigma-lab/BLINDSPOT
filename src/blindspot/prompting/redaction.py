"""Secret and hidden-state redaction for prompts."""

from __future__ import annotations

import re
from typing import Any

_HIDDEN_KEYS = frozenset({
    "grading_target", "attack_ground_truth", "unsafe_precursor_nodes",
    "point_of_no_return_step", "safe_target_state_hash", "forbidden_outcomes",
    "verifier_notes", "__hidden__", "__attack_id", "__payload_id",
    "is_injection", "malicious_goal", "is_chaining_attack",
})


def redact_hidden_labels(obj: Any) -> Any:
    """Recursively remove hidden/verifier keys from dicts."""
    if isinstance(obj, dict):
        return {
            k: redact_hidden_labels(v)
            for k, v in obj.items()
            if k not in _HIDDEN_KEYS and not str(k).startswith("__")
        }
    if isinstance(obj, list):
        return [redact_hidden_labels(item) for item in obj]
    return obj


def redact_secrets(text: str, patterns: list[str] | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Replace secret patterns in text with [REDACTED]. Return cleaned text and redaction log."""
    redactions: list[dict[str, Any]] = []
    if not patterns:
        return text, redactions
    for pattern in patterns:
        compiled = re.compile(pattern)
        matches = list(compiled.finditer(text))
        for match in matches:
            redactions.append({"pattern": pattern, "start": match.start(), "end": match.end()})
        text = compiled.sub("[REDACTED]", text)
    return text, redactions
