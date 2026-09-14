"""Horizon profile — multi-axis episode constraints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HorizonProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_interaction_steps: int
    max_tool_calls: int
    max_sessions: int = 1
    expected_tool_calls: int | None = None
    dependency_span: int | None = None
    dependency_breadth: int | None = None
    expected_state_mutations: int | None = None
    delayed_effect_gap: int | None = None
    max_simulated_time_seconds: int | None = None
    action_budget_by_actor: dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate(self) -> "HorizonProfile":
        if self.max_interaction_steps <= 0:
            raise ValueError("max_interaction_steps must be positive")
        if self.max_tool_calls <= 0:
            raise ValueError("max_tool_calls must be positive")
        if self.max_sessions <= 0:
            raise ValueError("max_sessions must be positive")
        if self.expected_tool_calls is not None:
            if self.expected_tool_calls > self.max_tool_calls:
                raise ValueError("expected_tool_calls must not exceed max_tool_calls")
        return self
