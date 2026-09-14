"""Permission and approval validators."""

from __future__ import annotations

from typing import TYPE_CHECKING

from blindspot.validators.base import BaseValidator
from blindspot.validators.reports import ValidationIssue

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle

_VALID_SUBJECT_TYPES = {"user", "group", "role", "agent"}


class PermissionValidator(BaseValidator):
    """Validates permission record consistency."""

    name = "permission_validator"

    def validate(self, bundle: "DomainStateBundle") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for pid, perm in bundle.permissions.items():
            if perm.subject_type not in _VALID_SUBJECT_TYPES:
                issues.append(ValidationIssue(
                    severity="error",
                    code="INVALID_SUBJECT_TYPE",
                    message=f"Permission {pid!r} has invalid subject_type {perm.subject_type!r}",
                    collection="permissions",
                    entity_id=pid,
                ))
            if perm.valid_from and perm.valid_until:
                if perm.valid_from >= perm.valid_until:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="INVALID_PERMISSION_WINDOW",
                        message=f"Permission {pid!r} valid_from >= valid_until",
                        collection="permissions",
                        entity_id=pid,
                    ))
            if not perm.permission.strip():
                issues.append(ValidationIssue(
                    severity="error",
                    code="EMPTY_PERMISSION_NAME",
                    message=f"Permission {pid!r} has empty permission name",
                    collection="permissions",
                    entity_id=pid,
                ))
        return issues


class ApprovalValidator(BaseValidator):
    """Validates approval record consistency."""

    name = "approval_validator"

    def validate(self, bundle: "DomainStateBundle") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for aid, approval in bundle.approvals.items():
            if not approval.action.strip():
                issues.append(ValidationIssue(
                    severity="error",
                    code="EMPTY_APPROVAL_ACTION",
                    message=f"Approval {aid!r} has empty action",
                    collection="approvals",
                    entity_id=aid,
                ))
            if approval.resource_id and approval.resource_id not in bundle.resources:
                issues.append(ValidationIssue(
                    severity="warning",
                    code="APPROVAL_RESOURCE_NOT_FOUND",
                    message=f"Approval {aid!r} resource_id {approval.resource_id!r} not found",
                    collection="approvals",
                    entity_id=aid,
                ))
        return issues
