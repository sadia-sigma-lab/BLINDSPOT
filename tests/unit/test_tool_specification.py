"""Unit tests for ToolSpecification validation."""

import pytest
from blindspot.core.identifiers import ComponentID
from blindspot.tools.specification import ToolSpecification


def _cid(name: str) -> ComponentID:
    return ComponentID(namespace="core", name=name, version="1.0.0")


def test_read_only_spec_valid():
    spec = ToolSpecification(
        tool_id=_cid("list-files"), display_name="List", description="d",
        read_scopes=["resources"], write_scopes=[],
        side_effect_level="none",
    )
    assert spec.side_effect_level == "none"


def test_mutating_without_write_scope_is_valid():
    spec = ToolSpecification(
        tool_id=_cid("share-file"), display_name="Share", description="d",
        read_scopes=["resources"], write_scopes=["resources"],
        side_effect_level="medium",
    )
    assert "resources" in spec.write_scopes


def test_read_only_with_write_scopes_fails():
    with pytest.raises(Exception):
        ToolSpecification(
            tool_id=_cid("bad-tool"), display_name="Bad", description="d",
            read_scopes=["resources"], write_scopes=["resources"],
            side_effect_level="none",  # contradiction
        )


def test_approval_required_without_action_fails():
    with pytest.raises(Exception):
        ToolSpecification(
            tool_id=_cid("share-file"), display_name="Share", description="d",
            read_scopes=["resources"], write_scopes=["resources"],
            side_effect_level="medium",
            requires_approval=True,  # no approval_action
        )


def test_approval_required_with_action_valid():
    spec = ToolSpecification(
        tool_id=_cid("share-file"), display_name="Share", description="d",
        read_scopes=["resources"], write_scopes=["resources"],
        side_effect_level="medium",
        requires_approval=True, approval_action="share",
    )
    assert spec.approval_action == "share"


def test_hidden_tool_visible_flag():
    spec = ToolSpecification(
        tool_id=_cid("hidden-tool"), display_name="H", description="d",
        read_scopes=[], write_scopes=[], side_effect_level="none",
        visibility="hidden",
    )
    from blindspot.tools.visibility import is_visible_to_agent
    assert not is_visible_to_agent(spec)
