"""Human review queue — for material disagreements that cannot be resolved automatically."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HumanReviewItem(BaseModel):
    model_config = ConfigDict(frozen=False)

    review_id: str
    verified_id: str
    question: str
    evidence_ids: list[str]
    judge_response_ids: list[str]
    priority: int = 5
    status: Literal["open", "assigned", "resolved", "dismissed"] = "open"


class HumanReviewQueue:
    """File-backed queue for human review items."""

    def __init__(self, queue_path: Path) -> None:
        self._path = queue_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._items: list[HumanReviewItem] = []
        if self._path.exists():
            self._load()

    def _load(self) -> None:
        for line in self._path.read_text().splitlines():
            if line.strip():
                self._items.append(HumanReviewItem(**json.loads(line)))

    def add(self, item: HumanReviewItem) -> None:
        self._items.append(item)
        with self._path.open("a") as f:
            f.write(json.dumps(item.model_dump()) + "\n")

    def list_open(self) -> list[HumanReviewItem]:
        return [i for i in self._items if i.status == "open"]

    def create_review(
        self,
        verified_id: str,
        question: str,
        evidence_ids: list[str],
        judge_response_ids: list[str],
        priority: int = 5,
    ) -> HumanReviewItem:
        item = HumanReviewItem(
            review_id=str(uuid.uuid4()),
            verified_id=verified_id,
            question=question,
            evidence_ids=evidence_ids,
            judge_response_ids=judge_response_ids,
            priority=priority,
        )
        self.add(item)
        return item
