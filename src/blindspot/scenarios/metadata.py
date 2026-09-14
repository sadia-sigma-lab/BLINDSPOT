"""Scenario metadata contract."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.identifiers import ComponentID


class ScenarioMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: ComponentID
    display_name: str
    description: str
    domain_id: str
    fixture_id: str
    template_id: str | None = None
    parent_scenario_ids: list[str] = Field(default_factory=list)
    version: str = "1.0.0"
    author: str = "benchmark-team"
    source: Literal["hand_authored", "generated", "mutated", "imported"] = "hand_authored"
    license: str = "Apache-2.0"
    tags: list[str] = Field(default_factory=list)
    benchmark_track: list[str] = Field(default_factory=list)
    deprecated: bool = False
