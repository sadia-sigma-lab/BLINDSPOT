"""Evidence extraction and model."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.prompting.redaction import redact_hidden_labels

_EVIDENCE_HIDDEN_KEYS = frozenset({
    "grading_target", "attack_ground_truth", "verifier_only",
    "verifier_notes", "__hidden__",
})


class EvidenceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    evidence_type: Literal[
        "trajectory_step", "tool_call", "tool_result", "state_diff",
        "state_snapshot", "audit_record", "policy_rule", "approval_record",
        "attack_trace", "prompt_excerpt", "model_response_excerpt",
        "event_record", "scenario_predicate",
    ]
    source_path: str
    step: int | None = None
    content: Any
    content_hash: str
    redacted: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


def extract_evidence(
    evidence_type: Literal[
        "trajectory_step", "tool_call", "tool_result", "state_diff",
        "state_snapshot", "audit_record", "policy_rule", "approval_record",
        "attack_trace", "prompt_excerpt", "model_response_excerpt",
        "event_record", "scenario_predicate",
    ],
    content: Any,
    source_path: str,
    step: int | None = None,
    redact: bool = True,
) -> EvidenceItem:
    """Extract a single evidence item, optionally redacting hidden fields."""
    import uuid
    if redact:
        content = redact_hidden_labels(content)

    content_str = json.dumps(content, sort_keys=True, default=str)
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    return EvidenceItem(
        evidence_id=str(uuid.uuid4()),
        evidence_type=evidence_type,
        source_path=source_path,
        step=step,
        content=content,
        content_hash=content_hash,
        redacted=redact,
    )
