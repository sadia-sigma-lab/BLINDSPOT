"""Minimal safe intervention selector."""

from __future__ import annotations

from typing import Any

from blindspot.interventions.catalog import ALL_INTERVENTIONS, Intervention
from blindspot.interventions.costs import InterventionCost
from blindspot.interventions.over_intervention import OverInterventionResult, check_over_intervention


class InterventionSelector:
    """Selects the minimum-cost intervention that prevents harm with sufficient utility."""

    def __init__(
        self,
        interventions: list[Intervention] | None = None,
        utility_threshold: float = 0.6,
    ) -> None:
        self._interventions = interventions or ALL_INTERVENTIONS
        self._utility_threshold = utility_threshold

    def select_minimal(
        self,
        snapshot: dict[str, Any],
        source_action: Any,
        scenario: Any,
        context: Any,
        source_goal_score: float = 1.0,
    ) -> tuple[Intervention | None, OverInterventionResult | None]:
        """Return (best_intervention, over_intervention_report)."""
        candidates: list[dict[str, Any]] = []

        for interv in self._interventions:
            if not interv.is_applicable(snapshot, source_action, scenario):
                continue
            try:
                app = interv.apply(snapshot, source_action, context)
            except Exception:
                continue

            total_cost = app.expected_cost_components.get("total", 0.0)
            blocked_utility = app.expected_cost_components.get("blocked_utility", 0.0)
            utility = max(0.0, 1.0 - blocked_utility)
            prevents_harm = interv.metadata.component_id.name not in ("allow",)

            candidates.append({
                "id": interv.metadata.component_id.name,
                "intervention": interv,
                "cost": total_cost,
                "utility_retention": utility,
                "prevents_harm": prevents_harm,
                "application": app,
            })

        if not candidates:
            return None, None

        # Select min-cost intervention that prevents harm and meets utility threshold
        safe_candidates = [
            c for c in candidates
            if c["prevents_harm"] and c["utility_retention"] >= self._utility_threshold
        ]

        if safe_candidates:
            best = min(safe_candidates, key=lambda x: x["cost"])
        else:
            # Fall back to safest regardless of utility
            best = min(candidates, key=lambda x: x["cost"])

        # Check over-intervention
        alternatives = [c for c in candidates if c["id"] != best["id"]]
        over = check_over_intervention(
            selected_id=best["id"],
            selected_cost=best["cost"],
            selected_utility=best["utility_retention"],
            selected_prevents_harm=best["prevents_harm"],
            alternatives=alternatives,
        )

        return best["intervention"], over
