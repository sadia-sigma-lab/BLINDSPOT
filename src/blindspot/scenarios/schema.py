"""Canonical scenario schema — the complete ScenarioSpec."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from blindspot.scenarios.actors import ScenarioActorSpec
from blindspot.scenarios.attacks import ScenarioAttackBinding
from blindspot.scenarios.decisions import CriticalDecisionPoint, SafeAlternative
from blindspot.scenarios.difficulty import DifficultyProfile
from blindspot.scenarios.events import ScenarioEventSpec
from blindspot.scenarios.goals import BenignTaskSpec
from blindspot.scenarios.hazards import HazardSpec
from blindspot.scenarios.horizons import HorizonProfile
from blindspot.scenarios.metadata import ScenarioMetadata
from blindspot.scenarios.outcomes import OutcomeSpec
from blindspot.scenarios.recovery import RecoverySpec
from blindspot.scenarios.splits import ScenarioSplitMetadata


class InitialStateSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_id: str
    fixture_version: str = "1.0.0"
    seed: int = 42
    overrides: list["StateOverride"] = Field(default_factory=list)
    generated_resources: list[dict[str, Any]] = Field(default_factory=list)


class StateOverride(BaseModel):
    model_config = ConfigDict(frozen=True)

    collection: str
    entity_id: str
    operation: str
    patch: dict[str, Any] = Field(default_factory=dict)


class PolicyBinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    policy_id: str
    version: str = "1.0.0"
    visible_to_actor_ids: list[str] = Field(default_factory=list)
    structured_enforcement: bool = True
    human_readable_available: bool = True
    priority_override: int | None = None


class ToolBindingSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    collection_id: str
    enabled_tool_ids: list[str]
    disabled_tool_ids: list[str] = Field(default_factory=list)
    actor_overrides: dict[str, list[str]] = Field(default_factory=dict)
    failure_profiles: dict[str, str] = Field(default_factory=dict)
    feature_flags: dict[str, bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _no_conflict(self) -> "ToolBindingSpec":
        conflicts = set(self.enabled_tool_ids) & set(self.disabled_tool_ids)
        if conflicts:
            raise ValueError(f"Tools are both enabled and disabled: {conflicts}")
        return self


class HiddenScenarioState(BaseModel):
    model_config = ConfigDict(frozen=True)

    grading_target: dict[str, Any] = Field(default_factory=dict)
    attack_ground_truth: dict[str, Any] = Field(default_factory=dict)
    unsafe_precursor_nodes: list[str] = Field(default_factory=list)
    point_of_no_return_step: int | None = None
    safe_target_state_hash: str | None = None
    forbidden_outcomes: list[str] = Field(default_factory=list)
    verifier_notes: dict[str, Any] = Field(default_factory=dict)


class FullScenarioSpec(BaseModel):
    """Complete declarative scenario specification."""

    model_config = ConfigDict(frozen=True)

    metadata: ScenarioMetadata
    initial_state: InitialStateSpec
    actors: list[ScenarioActorSpec]
    task: BenignTaskSpec
    policies: list[PolicyBinding] = Field(default_factory=list)
    tools: ToolBindingSpec
    attacks: list[ScenarioAttackBinding] = Field(default_factory=list)
    hazards: list[HazardSpec] = Field(default_factory=list)
    events: list[ScenarioEventSpec] = Field(default_factory=list)
    horizon: HorizonProfile
    decision_points: list[CriticalDecisionPoint] = Field(default_factory=list)
    safe_alternatives: list[SafeAlternative] = Field(default_factory=list)
    outcomes: OutcomeSpec
    recovery: RecoverySpec | None = None
    difficulty: DifficultyProfile = Field(default_factory=DifficultyProfile)
    splits: ScenarioSplitMetadata
    hidden: HiddenScenarioState = Field(default_factory=HiddenScenarioState)

    @model_validator(mode="after")
    def _unique_actor_ids(self) -> "FullScenarioSpec":
        ids = [a.actor_id for a in self.actors]
        if len(ids) != len(set(ids)):
            raise ValueError("Scenario actor_ids must be unique")
        return self
