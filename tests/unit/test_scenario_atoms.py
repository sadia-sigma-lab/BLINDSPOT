"""Unit tests for scenario atoms."""

from blindspot.scenarios.atoms import ALL_ATOMS, TASK_ATOMS, POLICY_ATOMS


def test_atoms_have_ids():
    for atom_id, atom in ALL_ATOMS.items():
        assert atom.atom_id
        assert atom.atom_type


def test_task_atom_has_capabilities():
    share = TASK_ATOMS["share_artifact"]
    assert "share-file" in share.required_capabilities


def test_policy_atoms_present():
    assert "deny_restricted_external" in POLICY_ATOMS
    assert "require_approval_confidential" in POLICY_ATOMS
