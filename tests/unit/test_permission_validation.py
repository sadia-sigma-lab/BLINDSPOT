"""Unit tests for permission and approval validators."""

import pytest
from datetime import datetime, timezone

from blindspot.data_model.permission import PermissionRecord
from blindspot.data_model.approval import ApprovalRecord
from blindspot.validators.permissions import PermissionValidator, ApprovalValidator

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_FUTURE = datetime(2027, 1, 1, tzinfo=timezone.utc)


def _make_bundle(permissions=None, approvals=None, resources=None, users=None):
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
    b = DomainStateBundle()
    if permissions:
        b.permissions = {p.entity_id: p for p in permissions}
    if approvals:
        b.approvals = {a.entity_id: a for a in approvals}
    if resources:
        b.resources = {r.entity_id: r for r in resources}
    if users:
        b.users = {u.entity_id: u for u in users}
    return b


def _perm(**kwargs):
    base = dict(entity_id="p1", schema_version="1.0.0", created_at=_NOW, updated_at=_NOW,
                subject_type="user", subject_id="u1", resource_id="r1",
                permission="read", granted_by="admin")
    base.update(kwargs)
    return PermissionRecord(**base)


def test_valid_permission_no_issues():
    b = _make_bundle(permissions=[_perm()])
    issues = PermissionValidator().validate(b)
    assert all(i.severity != "error" for i in issues)


def test_empty_permission_name_fails():
    b = _make_bundle(permissions=[_perm(permission="")])
    issues = PermissionValidator().validate(b)
    assert any(i.code == "EMPTY_PERMISSION_NAME" for i in issues)


def test_invalid_subject_type_detected_by_validator():
    # Pydantic catches invalid literals at construction time.
    # Verify the validator also reports INVALID_SUBJECT_TYPE when records exist
    # with a subject_type outside the canonical set (simulated via direct injection).
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
    from unittest.mock import MagicMock

    bad_perm = MagicMock()
    bad_perm.entity_id = "p_bad"
    bad_perm.subject_type = "robot"
    bad_perm.subject_id = "u1"
    bad_perm.resource_id = "r1"
    bad_perm.permission = "read"
    bad_perm.active = True
    bad_perm.valid_from = None
    bad_perm.valid_until = None
    bad_perm.is_active_at = lambda t: True

    b = DomainStateBundle()
    b.permissions["p_bad"] = bad_perm

    issues = PermissionValidator().validate(b)
    assert any(i.code == "INVALID_SUBJECT_TYPE" for i in issues)


def test_approval_empty_action_fails():
    ap = ApprovalRecord(entity_id="a1", schema_version="1.0.0", created_at=_NOW,
                        updated_at=_NOW, requester_id="u1", approver_id="u2",
                        action="", status="approved")
    b = _make_bundle(approvals=[ap])
    issues = ApprovalValidator().validate(b)
    assert any(i.code == "EMPTY_APPROVAL_ACTION" for i in issues)
