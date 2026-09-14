"""Termination and truncation logic."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from blindspot.simulation.budgets import EpisodeBudgetState


class TerminationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    terminated: bool = False
    truncated: bool = False
    reasons: list[str] = Field(default_factory=list)
    final_status: str | None = None


def check_termination(
    budget: EpisodeBudgetState,
    action_type: str | None,
    tool_success: bool | None,
    parse_failed: bool,
    fatal_error: bool,
) -> TerminationDecision:
    """Evaluate all termination and truncation conditions."""
    exhaustion = budget.any_exhausted()
    if exhaustion:
        return TerminationDecision(truncated=True, reasons=exhaustion, final_status="truncated")

    if action_type in ("message", "refuse", "escalate"):
        return TerminationDecision(terminated=True,
                                   reasons=["actor_sent_terminal_message"],
                                   final_status="completed")

    if fatal_error:
        return TerminationDecision(terminated=True,
                                   reasons=["fatal_runtime_error"],
                                   final_status="failed")

    if parse_failed:
        return TerminationDecision(truncated=True,
                                   reasons=["repeated_parse_failure"],
                                   final_status="truncated")

    return TerminationDecision()
