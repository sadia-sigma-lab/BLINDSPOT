"""Unit tests for rollback manager."""

import pytest
from blindspot.core.state import WorldState
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.transaction import TransactionManager
from blindspot.tools.rollback import RollbackManager
from blindspot.tools.runtime import make_context


def _state():
    return WorldState(
        schema_version="1.0", episode_id="e", step=0, session_id="s", random_seed=42,
        public={"resources": {"f1": {"name": "a.txt", "shared_with": []}}},
        private={}, hidden={}, audit_log=[],
    )


def test_rollback_restores_state():
    tm = TransactionManager()
    rm = RollbackManager()
    ctx = make_context(actor_id="user_alice", step=0, seed=42)

    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update",
        before={"name": "a.txt", "shared_with": []},
        after={"name": "a.txt", "shared_with": ["x@example.com"]},
        changed_fields=["shared_with"],
    )])
    state = _state()
    new_state, tx_result = tm.commit(state, plan, write_scopes=["resources"])
    assert new_state.public["resources"]["f1"]["shared_with"] == ["x@example.com"]

    token = rm.create_token(tx_result, "core:share-file@1.0.0", "user_alice")
    restored_state, rb_result, err = rm.rollback(new_state, token, "user_alice", ctx)
    assert err is None
    assert rb_result.committed
    assert restored_state.public["resources"]["f1"]["shared_with"] == []


def test_rollback_token_one_time_use():
    tm = TransactionManager()
    rm = RollbackManager()
    ctx = make_context(actor_id="user_alice", step=0, seed=42)

    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update", after={"name": "b.txt"},
    )])
    new_state, tx_result = tm.commit(_state(), plan, write_scopes=["resources"])
    token = rm.create_token(tx_result, "core:share-file@1.0.0", "user_alice")

    rm.rollback(new_state, token, "user_alice", ctx)
    _, _, err = rm.rollback(new_state, token, "user_alice", ctx)
    assert err is not None
    assert err.category == "conflict"


def test_wrong_actor_cannot_rollback():
    tm = TransactionManager()
    rm = RollbackManager()
    ctx = make_context(actor_id="attacker", step=0, seed=42)

    plan = MutationPlan(operations=[MutationOperation(
        collection="resources", entity_id="f1", operation="update", after={"name": "b.txt"},
    )])
    new_state, tx_result = tm.commit(_state(), plan, write_scopes=["resources"])
    token = rm.create_token(tx_result, "core:share-file@1.0.0", "user_alice")

    _, _, err = rm.rollback(new_state, token, "attacker", ctx)
    assert err is not None
    assert err.category == "authorization"
