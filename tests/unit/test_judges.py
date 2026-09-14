"""Unit tests for judge adapters, cache, and ensemble."""

import uuid
import pytest

from blindspot.judges.config import JudgeConfig
from blindspot.judges.request import JudgeRequest
from blindspot.judges.scripted import MockJudge, ScriptedJudge
from blindspot.judges.cache import JudgeCache
from blindspot.judges.ensemble import analyze_ensemble
from blindspot.verification.evidence import extract_evidence
from blindspot.verification.exceptions import JudgeError


def _config():
    return JudgeConfig(judge_id="test", adapter_id="mock", model_name="t", provider="local")


def _evidence():
    return [extract_evidence("state_snapshot", {"key": "value"}, "test", step=0)]


def _request(allowed: list[str] | None = None):
    ev = _evidence()
    return JudgeRequest(
        request_id=str(uuid.uuid4()),
        question_type="semantic_goal_completion",
        question="Did the agent complete the goal?",
        rubric=["Use only evidence."],
        evidence=ev,
        allowed_labels=allowed or ["completed", "not_completed"],
    )


def test_mock_judge_valid_label():
    judge = MockJudge()
    resp = judge.judge(_request(), _config())
    assert resp.label in ["completed", "not_completed"]


def test_judge_must_cite_evidence():
    from blindspot.judges.base import JudgeAdapter
    from blindspot.judges.request import JudgeResponse
    judge = MockJudge()
    req = _request()
    resp = judge.judge(req, _config())
    assert resp.cited_evidence_ids  # must not be empty


def test_invalid_label_rejected():
    judge = ScriptedJudge([{"label": "INVALID_LABEL"}])
    req = _request(["completed", "not_completed"])
    with pytest.raises(JudgeError):
        judge.judge(req, _config())


def test_cache_hit():
    cache = JudgeCache()
    judge = MockJudge()
    cfg = _config()
    req = _request()
    resp = judge.judge(req, cfg)
    cache.put(req, cfg, resp)
    cached = cache.get(req, cfg)
    assert cached is not None
    assert cached.response_id == resp.response_id


def test_disagreement_detected():
    from blindspot.judges.request import JudgeResponse
    responses = [
        JudgeResponse(response_id="r1", request_id="q", judge_id="j1",
                      label="completed", confidence=0.9,
                      rationale="x", cited_evidence_ids=["e1"]),
        JudgeResponse(response_id="r2", request_id="q", judge_id="j2",
                      label="not_completed", confidence=0.8,
                      rationale="y", cited_evidence_ids=["e1"]),
    ]
    ensemble = analyze_ensemble("q", responses)
    assert ensemble.material_disagreement


def test_consensus_detected():
    from blindspot.judges.request import JudgeResponse
    responses = [
        JudgeResponse(response_id="r1", request_id="q", judge_id="j1",
                      label="completed", confidence=0.9, rationale="x", cited_evidence_ids=["e1"]),
        JudgeResponse(response_id="r2", request_id="q", judge_id="j2",
                      label="completed", confidence=0.85, rationale="y", cited_evidence_ids=["e1"]),
    ]
    ensemble = analyze_ensemble("q", responses)
    assert not ensemble.material_disagreement
    assert ensemble.consensus_label == "completed"
