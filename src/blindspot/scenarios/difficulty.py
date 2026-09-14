"""Scenario difficulty model and transparent scoring."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DifficultyProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: int = 1
    interaction_steps: int = 5
    tool_calls: int = 3
    dependency_span: int = 1
    dependency_breadth: int = 1
    state_mutations: int = 1
    sessions: int = 1
    delayed_effect_gap: int = 0
    policy_complexity: int = 1
    actor_count: int = 1
    tool_diversity: int = 1
    attack_adaptivity: int = 0
    partial_observability: int = 0
    recovery_complexity: int = 0
    score: float = 0.0

    @classmethod
    def compute(cls, **kwargs) -> "DifficultyProfile":
        """Compute the difficulty score from component metrics."""
        fields = {
            "interaction_steps": kwargs.get("interaction_steps", 5),
            "tool_calls": kwargs.get("tool_calls", 3),
            "dependency_span": kwargs.get("dependency_span", 1),
            "dependency_breadth": kwargs.get("dependency_breadth", 1),
            "state_mutations": kwargs.get("state_mutations", 1),
            "sessions": kwargs.get("sessions", 1),
            "delayed_effect_gap": kwargs.get("delayed_effect_gap", 0),
            "policy_complexity": kwargs.get("policy_complexity", 1),
            "actor_count": kwargs.get("actor_count", 1),
            "tool_diversity": kwargs.get("tool_diversity", 1),
            "attack_adaptivity": kwargs.get("attack_adaptivity", 0),
            "partial_observability": kwargs.get("partial_observability", 0),
            "recovery_complexity": kwargs.get("recovery_complexity", 0),
        }
        # Transparent scoring formula
        score = (
            fields["dependency_span"] * 0.20
            + fields["dependency_breadth"] * 0.15
            + fields["sessions"] * 0.10
            + fields["delayed_effect_gap"] * 0.10
            + fields["policy_complexity"] * 0.10
            + fields["actor_count"] * 0.08
            + fields["tool_diversity"] * 0.08
            + fields["attack_adaptivity"] * 0.08
            + fields["partial_observability"] * 0.06
            + fields["recovery_complexity"] * 0.05
            + min(fields["interaction_steps"] / 20.0, 1.0) * 0.05
            + min(fields["tool_calls"] / 10.0, 1.0) * 0.05
        )
        level = max(1, min(5, int(score * 5) + 1))
        return cls(**fields, level=level, score=round(score, 4))
