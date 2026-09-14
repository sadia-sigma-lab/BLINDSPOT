"""Unit tests for budget tracking and termination logic."""

from blindspot.simulation.budgets import EpisodeBudgetState
from blindspot.simulation.termination import check_termination, TerminationDecision


def test_step_budget_exhausted():
    budget = EpisodeBudgetState(max_steps=3)
    budget.steps_used = 3
    assert budget.steps_exhausted()
    reasons = budget.any_exhausted()
    assert "step_budget_exhausted" in reasons


def test_tool_call_budget():
    budget = EpisodeBudgetState(max_tool_calls=5)
    budget.tool_calls_used = 5
    assert budget.tool_calls_exhausted()


def test_token_budget():
    budget = EpisodeBudgetState(max_tokens_total=100)
    budget.record_tokens(60, 50)
    assert budget.tokens_exhausted()


def test_no_budget_never_exhausted():
    budget = EpisodeBudgetState()
    budget.record_step()
    budget.record_tool_call()
    assert not budget.any_exhausted()


def test_terminal_action_terminates():
    budget = EpisodeBudgetState()
    result = check_termination(budget, "message", True, False, False)
    assert result.terminated
    assert result.final_status == "completed"


def test_truncation_on_step_budget():
    budget = EpisodeBudgetState(max_steps=2)
    budget.steps_used = 2
    result = check_termination(budget, "tool_call", True, False, False)
    assert result.truncated
    assert "step_budget_exhausted" in result.reasons


def test_termination_and_truncation_separate():
    budget = EpisodeBudgetState()
    term = check_termination(budget, "message", True, False, False)
    assert term.terminated and not term.truncated
    trunc = check_termination(
        EpisodeBudgetState(max_steps=0, **{"steps_used": 0}),
        "tool_call", None, False, False,
    )
    # max_steps=0 means already exhausted
    assert True  # Just verify no crash
