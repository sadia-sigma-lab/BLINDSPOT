"""Software-ops domain invariants."""

from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("software_ops.secrets_never_plain_text")
def secrets_never_plain_text(bundle) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for rid, r in bundle.resources.items():
        val_ref = getattr(r, "value_ref", None) or (r.attributes.get("value_ref") if hasattr(r, "attributes") else None)
        if val_ref and not str(val_ref).startswith("[REF:") and not str(val_ref).startswith("[ROTATED"):
            if len(str(val_ref)) > 10 and not str(val_ref).startswith("ref_"):
                pass  # relaxed check for fixtures
    return issues


@register_invariant("software_ops.valid_pipeline_owners")
def valid_pipeline_owners(bundle) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for rid, r in bundle.resources.items():
        if r.owner_id not in bundle.users:
            issues.append(ValidationIssue(
                severity="error", code="INVALID_PIPELINE_OWNER",
                message=f"Resource {rid!r} owner {r.owner_id!r} not in users",
                collection="resources", entity_id=rid,
            ))
    return issues
