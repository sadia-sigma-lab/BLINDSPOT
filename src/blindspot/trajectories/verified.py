"""Verified trajectory model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.adjudicators.base import AdjudicationResult
from blindspot.verification.config import VerificationStatus
from blindspot.verification.corrections import CorrectionProposal
from blindspot.verification.evidence import EvidenceItem
from blindspot.verification.findings import VerificationFinding
from blindspot.verification.quality import LabelConfidenceScore, TrajectoryQualityScore


class VerifiedTrajectory(BaseModel):
    model_config = ConfigDict(frozen=True)

    verified_id: str
    raw_run_id: str
    raw_manifest_hash: str
    verification_config_id: str
    verification_status: VerificationStatus
    findings: list[VerificationFinding]
    evidence_index: list[EvidenceItem]
    goal_result: dict[str, Any] = Field(default_factory=dict)
    harm_result: dict[str, Any] = Field(default_factory=dict)
    policy_result: dict[str, Any] = Field(default_factory=dict)
    attack_results: list[dict[str, Any]] = Field(default_factory=list)
    recovery_result: dict[str, Any] | None = None
    diagnostic_labels: list[str] = Field(default_factory=list)
    judge_request_ids: list[str] = Field(default_factory=list)
    judge_response_ids: list[str] = Field(default_factory=list)
    adjudications: list[AdjudicationResult] = Field(default_factory=list)
    correction_proposals: list[CorrectionProposal] = Field(default_factory=list)
    quality: TrajectoryQualityScore
    confidence: LabelConfidenceScore
    lineage: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
