"""Unit tests for scenario schema validation."""

import pytest
from blindspot.domains.minimal_workspace.scenarios.reference_families import (
    make_clean_external_sharing, make_task_injection,
)
from blindspot.scenarios.schema import ToolBindingSpec


def test_clean_scenario_valid():
    spec = make_clean_external_sharing()
    assert spec.metadata.scenario_id.name == "clean-external-sharing-001"


def test_duplicate_actor_ids_rejected():
    from blindspot.scenarios.schema import FullScenarioSpec
    from blindspot.domains.minimal_workspace.scenarios.reference_families import make_clean_external_sharing
    spec = make_clean_external_sharing()
    # Constructing with duplicate actor IDs must fail
    with pytest.raises(Exception):
        FullScenarioSpec(
            **{**spec.model_dump(), "actors": spec.actors + [spec.actors[0]]}
        )


def test_tool_binding_conflict_rejected():
    with pytest.raises(Exception):
        ToolBindingSpec(
            collection_id="test",
            enabled_tool_ids=["list-files"],
            disabled_tool_ids=["list-files"],  # conflict
        )


def test_invalid_horizon_rejected():
    from blindspot.scenarios.horizons import HorizonProfile
    with pytest.raises(Exception):
        HorizonProfile(max_interaction_steps=-1, max_tool_calls=5)


def test_expected_exceeds_max_rejected():
    from blindspot.scenarios.horizons import HorizonProfile
    with pytest.raises(Exception):
        HorizonProfile(max_interaction_steps=10, max_tool_calls=5, expected_tool_calls=10)
