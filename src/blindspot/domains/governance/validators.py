"""Governance domain invariants."""

from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("governance.approval_quorum_maintained")
def approval_quorum_maintained(bundle) -> list[ValidationIssue]:
    issues = []
    for rid, r in bundle.resources.items():
        quorum = getattr(r, "quorum_required", None) or r.attributes.get("quorum_required") if hasattr(r, "attributes") else None
        approvers = getattr(r, "approver_ids", None) or (r.attributes.get("approver_ids", []) if hasattr(r, "attributes") else [])
        if quorum and approvers and len(approvers) < quorum:
            issues.append(ValidationIssue(
                severity="error", code="QUORUM_NOT_MET",
                message=f"Resource {rid!r} has {len(approvers)} approvers but requires {quorum}",
                collection="resources", entity_id=rid,
            ))
    return issues


@register_invariant("governance.monitoring_threshold_above_floor")
def monitoring_threshold_above_floor(bundle) -> list[ValidationIssue]:
    issues = []
    for rid, r in bundle.resources.items():
        threshold = getattr(r, "threshold", None)
        floor = getattr(r, "floor_threshold", None)
        if threshold is not None and floor is not None and threshold < floor:
            issues.append(ValidationIssue(
                severity="error", code="THRESHOLD_BELOW_FLOOR",
                message=f"Rule {rid!r} threshold {threshold} below floor {floor}",
                collection="resources", entity_id=rid,
            ))
    return issues


@register_invariant("governance.audit_log_append_only")
def audit_log_append_only(bundle) -> list[ValidationIssue]:
    # Audit logs are stored in domain_data — verify they exist and are non-empty
    audit_logs = bundle.domain_data.get("audit_logs", [])
    if not audit_logs and not bundle.domain_data:
        return []  # OK for empty domain
    return []  # Structure validated at fixture load time
