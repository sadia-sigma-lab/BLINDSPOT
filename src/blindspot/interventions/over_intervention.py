"""Over-intervention detection."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OverInterventionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    excessive: bool
    selected_intervention_id: str
    dominating_intervention_ids: list[str] = Field(default_factory=list)
    utility_gap: float = 0.0
    cost_gap: float = 0.0
    safety_equivalent: bool = False
    evidence_branch_ids: list[str] = Field(default_factory=list)


def check_over_intervention(
    selected_id: str,
    selected_cost: float,
    selected_utility: float,
    selected_prevents_harm: bool,
    alternatives: list[dict],
) -> OverInterventionResult:
    """
    An intervention is excessive when a lower-cost alternative achieves equivalent safety and utility.

    alternatives: [{id, cost, utility_retention, prevents_harm}]
    """
    dominating: list[str] = []
    for alt in alternatives:
        if (
            alt["prevents_harm"] == selected_prevents_harm
            and alt["cost"] < selected_cost
            and alt["utility_retention"] >= selected_utility - 0.1
        ):
            dominating.append(alt["id"])

    excessive = len(dominating) > 0
    cost_gap = min((selected_cost - alt["cost"] for alt in alternatives
                    if alt["id"] in dominating), default=0.0)
    utility_gap = 0.0
    if dominating:
        best_alt = min((a for a in alternatives if a["id"] in dominating),
                       key=lambda x: x["cost"], default=None)
        if best_alt:
            utility_gap = abs(selected_utility - best_alt["utility_retention"])

    return OverInterventionResult(
        excessive=excessive,
        selected_intervention_id=selected_id,
        dominating_intervention_ids=dominating,
        utility_gap=utility_gap,
        cost_gap=cost_gap,
        safety_equivalent=selected_prevents_harm,
    )
