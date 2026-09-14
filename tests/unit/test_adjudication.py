"""Unit tests for adjudication."""

import uuid
from blindspot.adjudicators.rules import RuleBasedAdjudicator
from blindspot.judges.ensemble import analyze_ensemble, JudgeEnsembleResult
from blindspot.judges.request import JudgeResponse


def _resp(label: str, confidence: float = 0.9):
    return JudgeResponse(
        response_id=str(uuid.uuid4()), request_id="q",
        judge_id="j", label=label, confidence=confidence,
        rationale="test", cited_evidence_ids=["e1"],
    )


def test_deterministic_priority_wins():
    adj = RuleBasedAdjudicator()
    ensemble = analyze_ensemble("q", [_resp("not_completed"), _resp("not_completed")])
    result = adj.adjudicate(ensemble, deterministic_label="completed")
    assert result.final_label == "completed"
    assert result.basis == "deterministic_priority"
    assert result.confidence == 1.0


def test_majority_vote():
    adj = RuleBasedAdjudicator()
    ensemble = analyze_ensemble("q", [_resp("completed"), _resp("completed"), _resp("not_completed")])
    result = adj.adjudicate(ensemble)
    assert result.final_label == "completed"
    assert result.basis == "majority"


def test_unresolved_case_quarantined():
    adj = RuleBasedAdjudicator()
    ensemble = JudgeEnsembleResult(
        request_id="q",
        responses=[_resp("completed"), _resp("not_completed")],
        label_counts={"completed": 1, "not_completed": 1},
        confidence_summary={},
        agreement_rate=0.5,
        consensus_label=None,
        material_disagreement=True,
    )
    result = adj.adjudicate(ensemble)
    assert result.basis == "unresolved"
    assert result.final_label == "ambiguous"
