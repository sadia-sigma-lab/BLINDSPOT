"""Unit tests for visibility policy and state projection."""

import pytest
from datetime import datetime, timezone

from blindspot.core.state import WorldState
from blindspot.data_model.visibility import VisibilityPolicy, StateProjector

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _state():
    return WorldState(
        schema_version="1.0",
        episode_id="ep1",
        step=0,
        session_id="sess1",
        random_seed=42,
        public={
            "files": {"f1": {"name": "report.txt", "shared_with": []}},
            "users": {"u1": {"name": "Alice"}},
        },
        private={"internal_flag": True},
        hidden={"grading": {"target": "share_file"}, "attack_state": {"active": False}},
        audit_log=[],
    )


def test_hidden_state_never_exposed():
    state = _state()
    policy = VisibilityPolicy(
        actor_id="agent",
        readable_collections={"files", "users"},
        writable_collections=set(),
    )
    projector = StateProjector()
    projection = projector.project(state, "agent", policy)
    assert projection["hidden"] == {}
    assert "grading" not in str(projection)
    assert "attack_state" not in str(projection)


def test_unreadable_collection_excluded():
    state = _state()
    policy = VisibilityPolicy(
        actor_id="agent",
        readable_collections={"files"},  # no users
        writable_collections=set(),
    )
    projector = StateProjector()
    projection = projector.project(state, "agent", policy)
    assert "files" in projection["public"]
    assert "users" not in projection["public"]


def test_field_filter_applied():
    state = _state()
    policy = VisibilityPolicy(
        actor_id="agent",
        readable_collections={"files"},
        writable_collections=set(),
        field_filters={"files": ["shared_with"]},
    )
    projector = StateProjector()
    projection = projector.project(state, "agent", policy)
    f1 = projection["public"]["files"]["f1"]
    assert "shared_with" not in f1
    assert f1["name"] == "report.txt"


def test_projection_does_not_mutate_state():
    state = _state()
    original_hidden = dict(state.hidden)
    policy = VisibilityPolicy(
        actor_id="agent",
        readable_collections={"files"},
        writable_collections=set(),
    )
    StateProjector().project(state, "agent", policy)
    assert state.hidden == original_hidden


def test_projection_deterministic():
    state = _state()
    policy = VisibilityPolicy(
        actor_id="agent",
        readable_collections={"files", "users"},
        writable_collections=set(),
    )
    p = StateProjector()
    p1 = p.project(state, "agent", policy)
    p2 = p.project(state, "agent", policy)
    assert p1 == p2
