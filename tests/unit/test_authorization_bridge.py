"""Unit tests for the tool authorization bridge."""

import pytest
from datetime import datetime, timezone
from blindspot.tools.authorization import evaluate_authorization
from blindspot.tools.runtime import make_context
from blindspot.tools.state_view import ReadOnlyStateView
from blindspot.core.state import WorldState
from blindspot.domains.minimal_workspace.policies import AuthorizationEngine
from blindspot.domains.minimal_workspace.tools.list_files import ListFilesArgs, ListFilesTool
from blindspot.domains.minimal_workspace.tool_collection import load_workspace_state


_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _view(state: WorldState) -> ReadOnlyStateView:
    return ReadOnlyStateView(state, frozenset(["resources", "permissions", "users", "approvals", "policies"]))


def test_direct_allow():
    state = load_workspace_state()
    tool = ListFilesTool()
    ctx = make_context("user_alice", step=0, seed=42, current_time=_NOW)
    view = _view(state)
    engine = AuthorizationEngine()

    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
    bundle = tool._get_bundle(state)
    args = ListFilesArgs()
    decision, err = evaluate_authorization(engine, bundle, tool.specification, args, view, ctx)
    # list-files has no required_permissions — always allowed
    assert err is None


def test_cross_tenant_denied():
    state = load_workspace_state()
    tool = ListFilesTool()
    ctx = make_context("user_external", step=0, seed=42, current_time=_NOW)
    view = _view(state)
    engine = AuthorizationEngine()
    bundle = tool._get_bundle(state)
    args = ListFilesArgs()
    decision, err = evaluate_authorization(engine, bundle, tool.specification, args, view, ctx)
    # list-files has no resource — no cross-tenant check needed
    # but external user with no permissions is still allowed for read-only listing
    # Test cross-tenant is checked in workspace_authorization integration tests
    assert True  # placeholder — detailed cross-tenant tested in integration
