"""Scenario specification contract."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from blindspot.core.identifiers import ComponentID


class ScenarioSpec(BaseModel):
    """Declarative specification for one benchmark episode."""

    model_config = ConfigDict(frozen=True)

    scenario_id: ComponentID
    domain_id: ComponentID
    title: str
    description: str
    initial_state_path: str
    actors: list[dict[str, Any]]
    task: dict[str, Any]
    policies: list[str]
    attacks: list[dict[str, Any]] = []
    hazards: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    evaluators: list[str]
    horizon: dict[str, int]
    tags: list[str] = []
