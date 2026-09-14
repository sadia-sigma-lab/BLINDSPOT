"""Judge response cache — keyed by config+prompt+evidence hashes."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from blindspot.judges.config import JudgeConfig
from blindspot.judges.request import JudgeRequest, JudgeResponse


class JudgeCache:
    """In-memory file-backed judge response cache."""

    def __init__(self) -> None:
        self._store: dict[str, JudgeResponse] = {}

    def _key(self, request: JudgeRequest, config: JudgeConfig) -> str:
        payload = {
            "judge_id": config.judge_id,
            "model_name": config.model_name,
            "question_type": request.question_type,
            "question": request.question,
            "rubric": request.rubric,
            "allowed_labels": sorted(request.allowed_labels),
            "evidence_hashes": [e.content_hash for e in request.evidence],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

    def get(self, request: JudgeRequest, config: JudgeConfig) -> JudgeResponse | None:
        return self._store.get(self._key(request, config))

    def put(self, request: JudgeRequest, config: JudgeConfig, response: JudgeResponse) -> None:
        self._store[self._key(request, config)] = response

    def size(self) -> int:
        return len(self._store)
