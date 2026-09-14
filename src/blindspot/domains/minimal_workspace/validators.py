"""Domain-specific invariants for the minimal workspace domain."""

from __future__ import annotations

from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("minimal_workspace.unique_emails")
def unique_emails(bundle: "DomainStateBundle") -> list[ValidationIssue]:  # type: ignore[name-defined]
    """Email addresses must be unique across active users."""
    issues: list[ValidationIssue] = []
    seen: dict[str, str] = {}
    for uid, user in bundle.users.items():
        if user.email is None:
            continue
        email = user.email.lower()
        if email in seen:
            issues.append(ValidationIssue(
                severity="error",
                code="DUPLICATE_EMAIL",
                message=f"Users {uid!r} and {seen[email]!r} share email {email!r}",
                collection="users",
                entity_id=uid,
            ))
        else:
            seen[email] = uid
    return issues


@register_invariant("minimal_workspace.valid_file_owners")
def valid_file_owners(bundle: "DomainStateBundle") -> list[ValidationIssue]:  # type: ignore[name-defined]
    """All resource owners must be known users."""
    issues: list[ValidationIssue] = []
    for rid, resource in bundle.resources.items():
        if resource.owner_id not in bundle.users:
            issues.append(ValidationIssue(
                severity="error",
                code="INVALID_FILE_OWNER",
                message=f"Resource {rid!r} owner {resource.owner_id!r} not found in users",
                collection="resources",
                entity_id=rid,
            ))
    return issues


@register_invariant("minimal_workspace.valid_permission_targets")
def valid_permission_targets(bundle: "DomainStateBundle") -> list[ValidationIssue]:  # type: ignore[name-defined]
    """Permission resources must exist."""
    issues: list[ValidationIssue] = []
    for pid, perm in bundle.permissions.items():
        if perm.resource_id not in bundle.resources:
            issues.append(ValidationIssue(
                severity="error",
                code="PERMISSION_MISSING_RESOURCE",
                message=f"Permission {pid!r} references missing resource {perm.resource_id!r}",
                collection="permissions",
                entity_id=pid,
            ))
    return issues
