"""Unit tests for scenario composition."""

import pytest
from blindspot.scenarios.composer import ScenarioCompositionSpec, ScenarioComposer
from blindspot.scenarios.exceptions import ScenarioCompositionError


def test_compatible_atoms_compose():
    spec = ScenarioCompositionSpec(
        composition_id="c1",
        atom_ids=["locate_resource", "share_artifact"],
        generation_seed=42,
    )
    composer = ScenarioComposer()
    result = composer.compose(spec)
    assert "share-file" in result["required_capabilities"]


def test_missing_atom_raises():
    spec = ScenarioCompositionSpec(
        composition_id="c2",
        atom_ids=["nonexistent_atom_xyz"],
        generation_seed=42,
    )
    with pytest.raises(ScenarioCompositionError):
        ScenarioComposer().compose(spec)
