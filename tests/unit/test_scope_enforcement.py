"""Unit tests for scope enforcement."""

import pytest
from blindspot.core.state import WorldState
from blindspot.tools.state_view import ReadOnlyStateView, ScopeViolationError

from datetime import datetime, timezone


def _state():
    return WorldState(
        schema_version="1.0", episode_id="e", step=0, session_id="s",
        random_seed=42,
        public={"resources": {"f1": {"name": "a.txt"}}, "users": {"u1": {"name": "Alice"}}},
        private={}, hidden={"grading": {"secret": True}}, audit_log=[],
    )


def test_declared_read_passes():
    view = ReadOnlyStateView(_state(), frozenset(["resources"]))
    coll = view.get_collection("resources")
    assert "f1" in coll


def test_undeclared_read_fails():
    view = ReadOnlyStateView(_state(), frozenset(["resources"]))
    with pytest.raises(ScopeViolationError):
        view.get_collection("users")


def test_hidden_collection_always_fails():
    view = ReadOnlyStateView(_state(), frozenset(["resources", "grading", "hidden"]))
    with pytest.raises(ScopeViolationError):
        view.get_collection("grading")


def test_declared_write_passes():
    view = ReadOnlyStateView(_state(), frozenset(["resources"]))
    err = view.validate_write_scopes(["resources"], ["resources"])
    assert err is None


def test_undeclared_mutation_fails():
    view = ReadOnlyStateView(_state(), frozenset(["resources"]))
    err = view.validate_write_scopes(["users"], ["resources"])
    assert err is not None
    assert err.category == "scope"
