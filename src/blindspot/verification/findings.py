"""Verification finding model."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class VerificationFinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_id: str
    category: str
    severity: Literal["error", "warning", "info"]
    verdict: Literal["pass", "fail", "partial", "ambiguous", "not_applicable"]
    step: int | None = None
    actor_id: str | None = None
    predicate_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    source: Literal["deterministic", "judge", "adjudicator", "human"]
    confidence: float = 1.0
    details: dict[str, Any] = Field(default_factory=dict)


def _finding(
    category: str,
    verdict: Literal["pass", "fail", "partial", "ambiguous", "not_applicable"],
    severity: Literal["error", "warning", "info"],
    details: dict[str, Any] | None = None,
    step: int | None = None,
    evidence_ids: list[str] | None = None,
    confidence: float = 1.0,
    source: Literal["deterministic", "judge", "adjudicator", "human"] = "deterministic",
) -> VerificationFinding:
    import uuid
    return VerificationFinding(
        finding_id=str(uuid.uuid4()),
        category=category,
        severity=severity,
        verdict=verdict,
        step=step,
        evidence_ids=evidence_ids or [],
        source=source,
        confidence=confidence,
        details=details or {},
    )
