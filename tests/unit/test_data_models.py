"""Unit tests for shared canonical data models."""

import pytest
from datetime import datetime, timezone

from blindspot.data_model.base import BaseEntity
from blindspot.data_model.user import UserRecord
from blindspot.data_model.resource import ResourceRecord
from blindspot.data_model.permission import PermissionRecord
from blindspot.data_model.approval import ApprovalRecord
from blindspot.data_model.memory import MemoryRecord
from blindspot.data_model.policy import PolicyDocument, PolicyRule


_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_FUTURE = datetime(2027, 1, 1, tzinfo=timezone.utc)
_PAST = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _base_kwargs():
    return dict(
        entity_id="e1",
        schema_version="1.0.0",
        created_at=_NOW,
        updated_at=_NOW,
    )


def test_base_entity_requires_tz_aware():
    with pytest.raises(Exception):
        BaseEntity(entity_id="x", schema_version="1.0.0",
                   created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1))


def test_base_entity_empty_id_rejected():
    with pytest.raises(Exception):
        BaseEntity(entity_id="  ", schema_version="1.0.0", created_at=_NOW, updated_at=_NOW)


def test_resource_valid_classification():
    r = ResourceRecord(
        **_base_kwargs(),
        resource_type="file", owner_id="u1", organization_id="org1", classification="confidential"
    )
    assert r.classification == "confidential"


def test_resource_invalid_classification():
    with pytest.raises(Exception):
        ResourceRecord(
            **_base_kwargs(),
            resource_type="file", owner_id="u1", organization_id="org1", classification="topsecret"
        )


def test_permission_validity_window():
    perm = PermissionRecord(
        **_base_kwargs(),
        subject_type="user", subject_id="u1", resource_id="r1",
        permission="read", granted_by="admin",
        valid_from=_NOW, valid_until=_FUTURE,
    )
    assert perm.is_active_at(_NOW)
    assert not perm.is_active_at(_FUTURE)


def test_permission_invalid_window_raises():
    with pytest.raises(Exception):
        PermissionRecord(
            **_base_kwargs(),
            subject_type="user", subject_id="u1", resource_id="r1",
            permission="read", granted_by="admin",
            valid_from=_FUTURE, valid_until=_NOW,
        )


def test_approval_target_binding():
    ap = ApprovalRecord(
        **_base_kwargs(),
        requester_id="u1", approver_id="u2", action="share",
        resource_id="r1", target_id="x@example.com",
        status="approved", valid_until=_FUTURE,
    )
    assert ap.covers("share", "r1", "x@example.com")
    assert not ap.covers("share", "r1", "other@example.com")


def test_approval_expired():
    ap = ApprovalRecord(
        **_base_kwargs(),
        requester_id="u1", approver_id="u2", action="share",
        status="approved", valid_until=_NOW,
    )
    assert not ap.is_valid_at(_NOW)


def test_memory_confidence_bounds():
    with pytest.raises(Exception):
        MemoryRecord(
            **_base_kwargs(),
            owner_actor_id="u1", memory_type="episodic",
            content="test", confidence=1.5,
        )


def test_memory_expired():
    m = MemoryRecord(
        **_base_kwargs(),
        owner_actor_id="u1", memory_type="episodic",
        content="test", expires_at=_PAST,
    )
    assert m.is_expired_at(_NOW)


def test_policy_unique_rule_ids():
    with pytest.raises(Exception):
        PolicyDocument(
            **_base_kwargs(),
            title="P", domain="test",
            rules=[
                PolicyRule(rule_id="r1", description="", effect="allow", action_pattern="*"),
                PolicyRule(rule_id="r1", description="", effect="deny", action_pattern="*"),
            ],
        )
