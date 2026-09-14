"""Budget tracking for episodes."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EpisodeBudgetState(BaseModel):
    model_config = ConfigDict(frozen=False)

    steps_used: int = 0
    tool_calls_used: int = 0
    sessions_used: int = 1
    input_tokens: int = 0
    output_tokens: int = 0
    wall_time_seconds: float = 0.0

    max_steps: int = 20
    max_tool_calls: int = 10
    max_sessions: int = 1
    max_tokens_total: int | None = None
    max_wall_time_seconds: float | None = None

    def record_step(self) -> None:
        self.steps_used += 1

    def record_tool_call(self) -> None:
        self.tool_calls_used += 1

    def record_tokens(self, input_t: int, output_t: int) -> None:
        self.input_tokens += input_t
        self.output_tokens += output_t

    def steps_exhausted(self) -> bool:
        return self.steps_used >= self.max_steps

    def tool_calls_exhausted(self) -> bool:
        return self.tool_calls_used >= self.max_tool_calls

    def tokens_exhausted(self) -> bool:
        if self.max_tokens_total is None:
            return False
        return (self.input_tokens + self.output_tokens) >= self.max_tokens_total

    def wall_time_exhausted(self) -> bool:
        if self.max_wall_time_seconds is None:
            return False
        return self.wall_time_seconds >= self.max_wall_time_seconds

    def any_exhausted(self) -> list[str]:
        reasons = []
        if self.steps_exhausted():
            reasons.append("step_budget_exhausted")
        if self.tool_calls_exhausted():
            reasons.append("tool_call_budget_exhausted")
        if self.tokens_exhausted():
            reasons.append("token_budget_exhausted")
        if self.wall_time_exhausted():
            reasons.append("wall_time_exhausted")
        return reasons
