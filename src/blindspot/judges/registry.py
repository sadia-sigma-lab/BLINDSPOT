"""Judge adapter registry."""

from __future__ import annotations

from blindspot.judges.base import JudgeAdapter
from blindspot.judges.scripted import MockJudge, ScriptedJudge


class JudgeRegistry:
    def __init__(self) -> None:
        self._judges: dict[str, JudgeAdapter] = {}

    def register(self, judge: JudgeAdapter) -> None:
        self._judges[judge.judge_id] = judge

    def get(self, judge_id: str) -> JudgeAdapter:
        j = self._judges.get(judge_id)
        if j is None:
            raise KeyError(f"No judge registered for {judge_id!r}")
        return j

    def list(self) -> list[str]:
        return list(self._judges.keys())


def get_default_judge_registry() -> JudgeRegistry:
    reg = JudgeRegistry()
    reg.register(ScriptedJudge())
    reg.register(MockJudge())
    return reg
