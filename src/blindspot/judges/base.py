"""Abstract judge adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from blindspot.judges.config import JudgeConfig
from blindspot.judges.request import JudgeRequest, JudgeResponse
from blindspot.verification.exceptions import JudgeError


class JudgeAdapter(ABC):
    """Abstract interface for an LLM or scripted judge."""

    judge_id: str

    @abstractmethod
    def judge(self, request: JudgeRequest, config: JudgeConfig) -> JudgeResponse:
        ...

    def validate_response(self, response: JudgeResponse, request: JudgeRequest) -> None:
        """Raise if response uses invalid label or cites no evidence."""
        if response.label not in request.allowed_labels:
            raise JudgeError(
                f"Judge {self.judge_id!r} returned invalid label {response.label!r}; "
                f"allowed: {request.allowed_labels}"
            )
        if not response.cited_evidence_ids:
            raise JudgeError(
                f"Judge {self.judge_id!r} cited no evidence for request {request.request_id!r}"
            )
