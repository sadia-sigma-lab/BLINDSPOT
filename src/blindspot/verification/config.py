"""Verification pipeline configuration."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(str, Enum):
    ACCEPTED = "accepted"
    CONDITIONALLY_ACCEPTED = "conditionally_accepted"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


class VerificationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    config_id: str
    strict_integrity: bool = True
    require_replay_match: bool = True
    run_deterministic_checks: bool = True
    use_llm_judges: bool = True
    judge_ids: list[str] = Field(default_factory=list)
    min_judges_per_question: int = 2
    adjudicator_id: str = "default"
    cache_judge_responses: bool = True
    allow_correction_proposals: bool = True
    quarantine_on_replay_divergence: bool = True
    reject_on_checksum_failure: bool = True
    unresolved_policy: Literal[
        "quarantine", "accept_with_ambiguity", "reject"
    ] = "quarantine"
