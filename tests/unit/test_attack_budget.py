"""Unit tests for attack budget accounting."""

from blindspot.attacks.config import AttackBudget, AttackBudgetUsage
from blindspot.attacks.budget import check_budget


def test_within_budget():
    budget = AttackBudget(max_payloads=3)
    usage = AttackBudgetUsage(payloads=2)
    ok, reason = check_budget(usage, budget)
    assert ok


def test_payload_limit_exhausted():
    budget = AttackBudget(max_payloads=3)
    usage = AttackBudgetUsage(payloads=3)
    ok, reason = check_budget(usage, budget)
    assert not ok
    assert "payloads" in reason


def test_turn_limit_exhausted():
    budget = AttackBudget(max_turns=5)
    usage = AttackBudgetUsage(turns=5)
    ok, _ = check_budget(usage, budget)
    assert not ok


def test_no_limits_always_within():
    budget = AttackBudget()
    usage = AttackBudgetUsage(turns=9999, payloads=9999)
    ok, _ = check_budget(usage, budget)
    assert ok


def test_is_exhausted_method():
    budget = AttackBudget(max_payloads=2)
    usage = AttackBudgetUsage(payloads=2)
    assert usage.is_exhausted(budget)


def test_check_and_increment_respects_limit():
    budget = AttackBudget(max_payloads=1)
    usage = AttackBudgetUsage(payloads=1)
    result = usage.check_and_increment("payloads", budget)
    assert not result
