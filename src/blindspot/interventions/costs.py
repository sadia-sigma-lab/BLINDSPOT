"""Intervention cost decomposition."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InterventionCost(BaseModel):
    model_config = ConfigDict(frozen=True)

    latency: float = 0.0
    extra_steps: float = 0.0
    extra_tool_calls: float = 0.0
    user_burden: float = 0.0
    approval_burden: float = 0.0
    blocked_utility: float = 0.0
    false_positive_cost: float = 0.0
    operational_cost: float = 0.0
    total: float = 0.0

    @classmethod
    def from_components(cls, components: dict[str, float]) -> "InterventionCost":
        total = sum(components.values())
        return cls(**{k: components.get(k, 0.0) for k in cls.model_fields}, total=total)
