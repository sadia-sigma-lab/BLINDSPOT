"""Immutable attack trace storage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.config import AttackBudgetUsage
from blindspot.attacks.context import AttackContext
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.predicates import AttackPredicateResult
from blindspot.attacks.progress import AttackProgressResult
from blindspot.attacks.state import AttackState


class AttackTraceStep(BaseModel):
    """Immutable record of one attack lifecycle event."""

    model_config = ConfigDict(frozen=True)

    attack_instance_id: str
    step: int
    session_id: str
    hook: AttackHook
    visible_context_hash: str
    state_before: dict[str, Any]
    effect: dict[str, Any]
    state_after: dict[str, Any]
    budget_usage: AttackBudgetUsage
    progress: AttackProgressResult | None = None
    success: AttackPredicateResult | None = None
    provenance_ids: list[str] = Field(default_factory=list)


def _hash_context(context: AttackContext) -> str:
    payload = {
        "step": context.step,
        "session_id": context.session_id,
        "visible_tool_calls": context.visible_tool_calls,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]


class AttackTraceStore:
    """Append-only store for attack trace steps."""

    def __init__(self, run_dir: Path) -> None:
        self._run_dir = run_dir
        self._run_dir.mkdir(parents=True, exist_ok=True)

    def append_step(
        self,
        attack_id: str,
        step: AttackTraceStep,
    ) -> None:
        path = self._run_dir / f"attack_trace_{attack_id.replace(':', '_').replace('@', '_')}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(step.model_dump(), default=str) + "\n")

    def load_steps(self, attack_id: str) -> list[AttackTraceStep]:
        path = self._run_dir / f"attack_trace_{attack_id.replace(':', '_').replace('@', '_')}.jsonl"
        if not path.exists():
            return []
        steps: list[AttackTraceStep] = []
        for line in path.read_text().splitlines():
            if line.strip():
                steps.append(AttackTraceStep(**json.loads(line)))
        return steps
