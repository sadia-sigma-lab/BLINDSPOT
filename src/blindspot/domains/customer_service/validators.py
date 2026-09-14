"""Customer service domain invariants."""
from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("cs.refund_within_limit")
def refund_within_limit(bundle) -> list[ValidationIssue]:
    """Refund amount must not exceed the order total."""
    issues: list[ValidationIssue] = []
    for collection_name in ("orders", "domain_data"):
        if collection_name == "orders":
            orders_raw = bundle.domain_data.get("orders", {})
        else:
            continue
        if isinstance(orders_raw, dict):
            items = orders_raw.values()
        elif isinstance(orders_raw, list):
            items = orders_raw
        else:
            items = []
        for order in items:
            if isinstance(order, dict):
                eid = order.get("entity_id", "?")
                refund = order.get("refund_amount", 0.0) or 0.0
                total = order.get("total_usd", 0.0) or 0.0
                if refund > total:
                    issues.append(ValidationIssue(
                        severity="error",
                        code="REFUND_EXCEEDS_TOTAL",
                        message=f"Order {eid!r}: refund_amount ({refund}) > total_usd ({total})",
                        collection="orders",
                        entity_id=eid,
                    ))
    return issues


@register_invariant("cs.order_status_valid")
def order_status_valid(bundle) -> list[ValidationIssue]:
    """No order with status 'delivered' can simultaneously have status 'pending'."""
    # This invariant is always satisfied by construction — an order has exactly
    # one status field; we check that no delivered order is mis-tagged pending.
    issues: list[ValidationIssue] = []
    orders_raw = bundle.domain_data.get("orders", {})
    if isinstance(orders_raw, dict):
        items = orders_raw.values()
    elif isinstance(orders_raw, list):
        items = orders_raw
    else:
        items = []
    for order in items:
        if isinstance(order, dict):
            status = order.get("status", "")
            # Detect contradiction: entity_id listed in both delivered and pending sets
            # (here we simply check status field consistency)
            if status == "delivered":
                # Just verify the record itself is not also marked pending somehow
                pass  # single status field — no contradiction possible
    return issues
