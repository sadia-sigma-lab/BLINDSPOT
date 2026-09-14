"""Judge request and response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.verification.evidence import EvidenceItem


class JudgeRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_id: str
    question_type: str
    question: str
    rubric: list[str]
    evidence: list[EvidenceItem]
    allowed_labels: list[str]
    scenario_context: dict[str, Any] = Field(default_factory=dict)


class JudgeResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    response_id: str
    request_id: str
    judge_id: str
    label: str
    confidence: float
    rationale: str
    cited_evidence_ids: list[str]
    uncertainties: list[str] = Field(default_factory=list)
    raw_response: Any = None
    usage: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = None
    error: dict[str, Any] | None = None
