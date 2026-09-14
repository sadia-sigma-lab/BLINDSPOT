"""Unit tests for the transaction manager."""

import pytest
from blindspot.core.state import WorldState
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.transaction import TransactionManager


def _state():
    return WorldState(
        schema_version="1.0", episode_id="e", step=0, session_id="s", random_seed=42,
        public={"resources": {"f1": {"name": "a.txt", "shared_with": []}}},
        private={}, hidden={}, audit_log=[],
    )


def test_successful_commit():
    tm = TransactionManager()
    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update",
        after={"name": "b.txt"}, changed_fields=["name"],
    )])
    new_state, result = tm.commit(_state(), plan, write_scopes=["resources"])
    assert result.committed
    assert new_state.public["resources"]["f1"]["name"] == "b.txt"


def test_failed_validation_leaves_state_unchanged():
    tm = TransactionManager()
    plan = MutationPlan(operations=[MutationOperation(
        collection="hidden_illegal", entity_id="x", operation="create", after={"x": 1},
    )])
    original = _state()
    new_state, result = tm.commit(original, plan, write_scopes=["resources"])
    assert not result.committed
    assert new_state.public == original.public


def test_scope_violation_blocked():
    tm = TransactionManager()
    plan = MutationPlan(operations=[MutationOperation(
        collection="unauthorized", entity_id="u1", operation="create", after={"y": 2},
    )])
    _, result = tm.commit(_state(), plan, write_scopes=["resources"])
    assert not result.committed


def test_normalized_diff_correct():
    tm = TransactionManager()
    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update",
        before={"name": "a.txt", "shared_with": []},
        after={"name": "a.txt", "shared_with": ["x@example.com"]},
        changed_fields=["shared_with"],
    )])
    _, result = tm.commit(_state(), plan, write_scopes=["resources"])
    assert result.committed
    assert len(result.state_diff.mutations) == 1
    assert result.state_diff.mutations[0].operation == "replace"


def test_pre_post_hashes_differ_on_mutation():
    tm = TransactionManager()
    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update",
        after={"name": "changed.txt"},
    )])
    _, result = tm.commit(_state(), plan, write_scopes=["resources"])
    assert result.pre_state_hash != result.post_state_hash
