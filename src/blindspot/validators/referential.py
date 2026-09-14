"""Referential integrity validator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from blindspot.validators.base import BaseValidator
from blindspot.validators.reports import ValidationIssue

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle


class ReferentialIntegrityValidator(BaseValidator):
    """Checks cross-collection foreign-key constraints."""

    name = "referential_integrity"

    def validate(self, bundle: "DomainStateBundle") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Resource owners must exist
        for rid, resource in bundle.resources.items():
            if resource.owner_id not in bundle.users:
                issues.append(ValidationIssue(
                    severity="error",
                    code="INVALID_RESOURCE_OWNER",
                    message=f"Resource {rid!r} owner {resource.owner_id!r} not in users",
                    collection="resources",
                    entity_id=rid,
                ))

        # Permission subjects
        for pid, perm in bundle.permissions.items():
            if perm.subject_type == "user" and perm.subject_id not in bundle.users:
                issues.append(ValidationIssue(
                    severity="error",
                    code="INVALID_PERMISSION_SUBJECT",
                    message=f"Permission {pid!r} subject {perm.subject_id!r} not in users",
                    collection="permissions",
                    entity_id=pid,
                ))
            if perm.resource_id not in bundle.resources:
                issues.append(ValidationIssue(
                    severity="error",
                    code="INVALID_PERMISSION_RESOURCE",
                    message=f"Permission {pid!r} resource {perm.resource_id!r} not found",
                    collection="permissions",
                    entity_id=pid,
                ))

        # Approval approvers must be users
        for aid, approval in bundle.approvals.items():
            if approval.approver_id not in bundle.users:
                issues.append(ValidationIssue(
                    severity="error",
                    code="INVALID_APPROVAL_APPROVER",
                    message=f"Approval {aid!r} approver {approval.approver_id!r} not in users",
                    collection="approvals",
                    entity_id=aid,
                ))

        # Message attachment ids must exist in resources
        for mid, msg in bundle.messages.items():
            for att_id in msg.attachment_ids:
                if att_id not in bundle.resources:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="INVALID_MESSAGE_ATTACHMENT",
                        message=f"Message {mid!r} attachment {att_id!r} not in resources",
                        collection="messages",
                        entity_id=mid,
                    ))

        return issues
