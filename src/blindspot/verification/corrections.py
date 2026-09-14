"""Correction proposal model — never modifies raw data."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CorrectionProposal(BaseModel):
    model_config = ConfigDict(frozen=False)

    proposal_id: str
    raw_run_id: str
    target_artifact: str
    target_step: int | None = None
    correction_type: Literal[
        "parse_normalization", "label_change", "missing_reference",
        "metadata_fix", "state_diff_reconstruction", "judge_annotation",
    ]
    before: Any
    proposed_after: Any
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)
    proposer: str = "verification_pipeline"
    status: Literal["proposed", "accepted", "rejected", "superseded"] = "proposed"
