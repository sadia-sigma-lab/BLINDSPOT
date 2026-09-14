"""Budget accounting helpers."""

from blindspot.attacks.config import AttackBudget, AttackBudgetUsage


def check_budget(usage: AttackBudgetUsage, budget: AttackBudget) -> tuple[bool, str]:
    """Return (within_budget, reason). reason is empty when within budget."""
    for field in ("turns", "payloads", "tool_influences", "memory_writes",
                  "sessions", "tokens", "optimization_steps"):
        limit = getattr(budget, f"max_{field}", None)
        if limit is not None and getattr(usage, field) >= limit:
            return False, f"{field} limit {limit} reached"
    return True, ""
