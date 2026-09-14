"""Attack configuration and budget models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from blindspot.attacks.taxonomy import AttackerKnowledgeTier


class AttackBudget(BaseModel):
    """Resource limits for one attack instance."""

    model_config = ConfigDict(frozen=True)

    max_turns: int | None = None
    max_payloads: int | None = None
    max_tool_influences: int | None = None
    max_memory_writes: int | None = None
    max_sessions: int | None = None
    max_tokens: int | None = None
    max_optimization_steps: int | None = None


class AttackBudgetUsage(BaseModel):
    """Running usage counters for one attack instance."""

    model_config = ConfigDict(frozen=False)

    turns: int = 0
    payloads: int = 0
    tool_influences: int = 0
    memory_writes: int = 0
    sessions: int = 0
    tokens: int = 0
    optimization_steps: int = 0

    def check_and_increment(self, field: str, budget: AttackBudget) -> bool:
        """Increment counter; return False if limit would be exceeded."""
        limit = getattr(budget, f"max_{field}", None)
        current = getattr(self, field, 0)
        if limit is not None and current >= limit:
            return False
        setattr(self, field, current + 1)
        return True

    def is_exhausted(self, budget: AttackBudget) -> bool:
        for field in ("turns", "payloads", "tool_influences", "memory_writes",
                      "sessions", "tokens", "optimization_steps"):
            limit = getattr(budget, f"max_{field}", None)
            if limit is not None and getattr(self, field) >= limit:
                return True
        return False


class AttackConfig(BaseModel):
    """Per-scenario configuration for one attack instance."""

    model_config = ConfigDict(frozen=True)

    attack_id: str
    enabled: bool = True
    seed: int = 42
    source_actor_id: str | None = None
    target_actor_id: str
    knowledge_tier: AttackerKnowledgeTier = AttackerKnowledgeTier.TOOL_CALLS
    budget: AttackBudget = Field(default_factory=AttackBudget)
    activation: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    success_predicates: list[str] = Field(default_factory=list)
    abort_predicates: list[str] = Field(default_factory=list)
    clean_control_id: str | None = None
