"""CleanTrajectory schema — the final publication-ready artifact."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ConversationTurn(BaseModel):
    model_config = ConfigDict(frozen=True)
    turn: int
    role: Literal["user", "assistant", "tool_result"]
    content: str
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    is_attack_turn: bool = False


class JudgeScores(BaseModel):
    model_config = ConfigDict(frozen=True)
    attack_realism: int = 0
    agent_safety: str = "ambiguous"
    benign_utility: int = 0
    turn_coherence: int = 0
    tool_correctness: int = 0
    label_confidence: float = 0.0
    judge_model: str = ""


class CleanTrajectoryLineage(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_run_id: str
    scenario_id: str
    attack_family: str
    seed: int
    user_model: str
    execution_model: str
    judge_model: str
    corrections_applied: list[str] = Field(default_factory=list)


class CleanTrajectory(BaseModel):
    model_config = ConfigDict(frozen=False)

    clean_id: str
    source_trajectory_id: str
    scenario_id: str
    attack_family: str | None = None
    episode_type: Literal["benign", "adversarial_unsafe", "adversarial_safe", "hazard"] = "benign"
    turns: int = 0
    tool_calls: int = 0
    safety_label: Literal["safe_completion", "unsafe_completion", "correct_refusal", "indeterminate", "over_refusal"] = "indeterminate"
    diagnostic_labels: list[str] = Field(default_factory=list)
    judge_scores: JudgeScores = Field(default_factory=JudgeScores)
    judge_notes: str = ""
    corrections_applied: list[str] = Field(default_factory=list)
    human_reviewed: bool = False
    publishable: bool = False
    conversation_transcript: str = ""
    tool_calls_summary: list[str] = Field(default_factory=list)
    lineage: CleanTrajectoryLineage | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def to_training_record(self) -> dict[str, Any]:
        """Export as a training data record."""
        return {
            "id": self.clean_id,
            "scenario_id": self.scenario_id,
            "attack_family": self.attack_family,
            "episode_type": self.episode_type,
            "safety_label": self.safety_label,
            "turns": self.turns,
            "tool_calls": self.tool_calls,
            "conversation": self.conversation_transcript,
            "diagnostic_labels": self.diagnostic_labels,
            "judge_scores": self.judge_scores.model_dump() if self.judge_scores else {},
            "lineage": self.lineage.model_dump() if self.lineage else {},
        }
