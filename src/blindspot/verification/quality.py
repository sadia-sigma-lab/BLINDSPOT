"""Quality and confidence scoring."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TrajectoryQualityScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    integrity: float = 0.0
    replay: float = 0.0
    completeness: float = 0.0
    evaluator_coverage: float = 0.0
    judge_agreement: float = 0.0
    evidence_quality: float = 0.0
    reproducibility: float = 0.0
    overall: float = 0.0


class LabelConfidenceScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    goal: float = 0.0
    harm: float = 0.0
    policy: float = 0.0
    attack: float = 0.0
    recovery: float = 0.0
    diagnostic: float = 0.0


def compute_quality(
    integrity_ok: bool,
    replay_ok: bool,
    steps_count: int,
    evaluator_count: int,
    judge_agreement: float,
    evidence_items: int,
) -> TrajectoryQualityScore:
    integrity = 1.0 if integrity_ok else 0.0
    replay = 1.0 if replay_ok else 0.0
    completeness = min(1.0, steps_count / 5.0)
    evaluator_coverage = min(1.0, evaluator_count / 5.0)
    evidence_quality = min(1.0, evidence_items / 3.0)
    reproducibility = 1.0 if integrity_ok and replay_ok else 0.5

    overall = (
        integrity * 0.25 + replay * 0.25 + completeness * 0.10
        + evaluator_coverage * 0.15 + judge_agreement * 0.10
        + evidence_quality * 0.10 + reproducibility * 0.05
    )
    return TrajectoryQualityScore(
        integrity=integrity, replay=replay, completeness=completeness,
        evaluator_coverage=evaluator_coverage, judge_agreement=judge_agreement,
        evidence_quality=evidence_quality, reproducibility=reproducibility,
        overall=round(overall, 4),
    )


def compute_confidence(
    goal_confident: bool,
    harm_confident: bool,
    policy_confident: bool,
    attack_confident: bool,
    recovery_confident: bool,
    diagnostic_confident: bool,
) -> LabelConfidenceScore:
    return LabelConfidenceScore(
        goal=1.0 if goal_confident else 0.5,
        harm=1.0 if harm_confident else 0.5,
        policy=1.0 if policy_confident else 0.5,
        attack=1.0 if attack_confident else 0.5,
        recovery=1.0 if recovery_confident else 0.5,
        diagnostic=1.0 if diagnostic_confident else 0.5,
    )
