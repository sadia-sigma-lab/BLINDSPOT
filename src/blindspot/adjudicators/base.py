"""Adjudication result and abstract interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.judges.ensemble import JudgeEnsembleResult


class AdjudicationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    adjudication_id: str
    request_id: str
    final_label: str
    confidence: float
    basis: Literal[
        "deterministic_priority", "majority", "weighted_vote",
        "secondary_judge", "human_review", "unresolved",
    ]
    accepted_evidence_ids: list[str] = Field(default_factory=list)
    rejected_response_ids: list[str] = Field(default_factory=list)
    rationale: str


class Adjudicator(ABC):
    adjudicator_id: str

    @abstractmethod
    def adjudicate(
        self,
        ensemble: JudgeEnsembleResult,
        deterministic_label: str | None = None,
    ) -> AdjudicationResult:
        ...
