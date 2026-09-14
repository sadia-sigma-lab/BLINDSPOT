"""Scenario card generation."""

from __future__ import annotations

from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from blindspot.scenarios.schema import FullScenarioSpec


class ScenarioCard(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: str
    title: str
    domain: str
    benign_goal: str
    attack_family: str | None = None
    hazard_family: str | None = None
    horizon: dict[str, Any] = Field(default_factory=dict)
    critical_decisions: list[str] = Field(default_factory=list)
    safe_twin: str | None = None
    evaluator_types: list[str] = Field(default_factory=list)
    intended_tracks: list[str] = Field(default_factory=list)


def generate_card(spec: FullScenarioSpec) -> ScenarioCard:
    """Generate a scenario card from a FullScenarioSpec."""
    attack_family: str | None = None
    if spec.attacks:
        first = spec.attacks[0]
        # Extract family from attack_id format: namespace:family@version
        parts = first.attack_id.split(":")
        if len(parts) > 1:
            attack_family = parts[1].split("@")[0]

    horizon_dict = {
        "max_steps": spec.horizon.max_interaction_steps,
        "max_tool_calls": spec.horizon.max_tool_calls,
        "dependency_span": spec.horizon.dependency_span,
        "sessions": spec.horizon.max_sessions,
    }

    return ScenarioCard(
        scenario_id=spec.metadata.scenario_id.canonical(),
        title=spec.metadata.display_name,
        domain=spec.metadata.domain_id,
        benign_goal=spec.task.instruction,
        attack_family=attack_family,
        horizon=horizon_dict,
        critical_decisions=[d.decision_id for d in spec.decision_points],
        evaluator_types=["deterministic"],
        intended_tracks=spec.metadata.benchmark_track,
    )


def card_to_yaml(card: ScenarioCard) -> str:
    return yaml.dump({"scenario_card": card.model_dump()}, default_flow_style=False)
