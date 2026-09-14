"""Finance domain invariants."""
from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("finance.pii_always_redacted")
def pii_always_redacted(bundle):
    issues = []
    for rid, r in bundle.resources.items():
        if hasattr(r, 'pii_type') and not getattr(r, 'redacted', True):
            issues.append(ValidationIssue(
                severity="error", code="PII_NOT_REDACTED",
                message=f"PII record {rid!r} is not redacted",
                collection="resources", entity_id=rid,
            ))
    return issues


@register_invariant("finance.valid_account_owners")
def valid_account_owners(bundle):
    issues = []
    for rid, r in bundle.resources.items():
        if r.owner_id not in bundle.users:
            issues.append(ValidationIssue(
                severity="error", code="INVALID_ACCOUNT_OWNER",
                message=f"Resource {rid!r} owner {r.owner_id!r} not in users",
                collection="resources", entity_id=rid,
            ))
    return issues
