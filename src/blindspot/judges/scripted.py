"""Scripted and mock judge adapters — deterministic, for testing."""

from __future__ import annotations

import uuid
from typing import Any

from blindspot.judges.base import JudgeAdapter
from blindspot.judges.config import JudgeConfig
from blindspot.judges.request import JudgeRequest, JudgeResponse


class ScriptedJudge(JudgeAdapter):
    """Returns a fixed sequence of responses — for testing."""

    judge_id = "scripted"

    def __init__(self, script: list[dict[str, Any]] | None = None) -> None:
        self._script = script or []
        self._index = 0

    def set_script(self, script: list[dict[str, Any]]) -> None:
        self._script = script
        self._index = 0

    def judge(self, request: JudgeRequest, config: JudgeConfig) -> JudgeResponse:
        if not self._script:
            entry: dict[str, Any] = {}
        else:
            entry = self._script[min(self._index, len(self._script) - 1)]
            self._index += 1

        label = entry.get("label", request.allowed_labels[0] if request.allowed_labels else "pass")
        evidence_ids = (
            entry.get("cited_evidence_ids")
            or [e.evidence_id for e in request.evidence[:1]]
        )

        response = JudgeResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            judge_id=self.judge_id,
            label=label,
            confidence=entry.get("confidence", 0.9),
            rationale=entry.get("rationale", "Scripted response."),
            cited_evidence_ids=evidence_ids,
            uncertainties=entry.get("uncertainties", []),
            raw_response=entry,
            usage={"input_tokens": 0, "output_tokens": 0},
        )
        self.validate_response(response, request)
        return response


class MockJudge(JudgeAdapter):
    """Always returns the first allowed label with a fixed confidence."""

    judge_id = "mock"

    def judge(self, request: JudgeRequest, config: JudgeConfig) -> JudgeResponse:
        label = request.allowed_labels[0] if request.allowed_labels else "pass"
        ev_ids = [e.evidence_id for e in request.evidence[:1]]
        response = JudgeResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            judge_id=self.judge_id,
            label=label,
            confidence=0.8,
            rationale="Mock judge: first allowed label.",
            cited_evidence_ids=ev_ids if ev_ids else ["mock-evidence"],
            raw_response=None,
        )
        return response
