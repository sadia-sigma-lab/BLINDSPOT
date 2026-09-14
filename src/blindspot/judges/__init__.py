"""Judge subsystem."""

from blindspot.judges.base import JudgeAdapter
from blindspot.judges.config import JudgeConfig
from blindspot.judges.request import JudgeRequest, JudgeResponse
from blindspot.judges.scripted import ScriptedJudge, MockJudge
from blindspot.judges.cache import JudgeCache
from blindspot.judges.ensemble import JudgeEnsembleResult, analyze_ensemble
from blindspot.judges.registry import JudgeRegistry, get_default_judge_registry

__all__ = [
    "JudgeAdapter", "JudgeConfig", "JudgeRequest", "JudgeResponse",
    "ScriptedJudge", "MockJudge", "JudgeCache",
    "JudgeEnsembleResult", "analyze_ensemble",
    "JudgeRegistry", "get_default_judge_registry",
]
