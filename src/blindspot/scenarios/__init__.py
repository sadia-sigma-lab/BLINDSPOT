"""Scenario authoring and generation subsystem."""

from blindspot.scenarios.schema import FullScenarioSpec, InitialStateSpec, ToolBindingSpec, PolicyBinding, HiddenScenarioState
from blindspot.scenarios.metadata import ScenarioMetadata
from blindspot.scenarios.registry import ScenarioRegistry
from blindspot.scenarios.validation import validate_scenario, ScenarioValidationReport

__all__ = [
    "FullScenarioSpec", "InitialStateSpec", "ToolBindingSpec", "PolicyBinding",
    "HiddenScenarioState", "ScenarioMetadata", "ScenarioRegistry",
    "validate_scenario", "ScenarioValidationReport",
]
