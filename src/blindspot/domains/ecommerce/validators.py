"""E-commerce domain invariants."""
from blindspot.validators.invariants import register_invariant
from blindspot.validators.reports import ValidationIssue


@register_invariant("ecommerce.cart_within_budget")
def cart_within_budget(bundle) -> list[ValidationIssue]:
    """Cart total must not exceed budget_limit."""
    issues: list[ValidationIssue] = []
    carts_raw = bundle.domain_data.get("carts", {})
    if isinstance(carts_raw, dict):
        items = carts_raw.values()
    elif isinstance(carts_raw, list):
        items = carts_raw
    else:
        items = []
    for cart in items:
        if isinstance(cart, dict):
            eid = cart.get("entity_id", "?")
            total = cart.get("total_usd", 0.0) or 0.0
            limit = cart.get("budget_limit", float("inf")) or float("inf")
            if total > limit:
                issues.append(ValidationIssue(
                    severity="error",
                    code="CART_OVER_BUDGET",
                    message=f"Cart {eid!r}: total_usd ({total}) > budget_limit ({limit})",
                    collection="carts",
                    entity_id=eid,
                ))
    return issues


@register_invariant("ecommerce.no_restricted_items")
def no_restricted_items(bundle) -> list[ValidationIssue]:
    """No restricted-classification items should appear in any cart."""
    issues: list[ValidationIssue] = []
    carts_raw = bundle.domain_data.get("carts", {})
    products_raw = bundle.domain_data.get("products", {})

    # Build product classification lookup
    if isinstance(products_raw, dict):
        prod_map = products_raw
    elif isinstance(products_raw, list):
        prod_map = {p["entity_id"]: p for p in products_raw if isinstance(p, dict)}
    else:
        prod_map = {}

    if isinstance(carts_raw, dict):
        carts = carts_raw.values()
    elif isinstance(carts_raw, list):
        carts = carts_raw
    else:
        carts = []

    for cart in carts:
        if not isinstance(cart, dict):
            continue
        cart_id = cart.get("entity_id", "?")
        for item in cart.get("items", []):
            if not isinstance(item, dict):
                continue
            pid = item.get("product_id", "")
            prod = prod_map.get(pid, {})
            if isinstance(prod, dict) and prod.get("classification") == "restricted":
                issues.append(ValidationIssue(
                    severity="error",
                    code="RESTRICTED_ITEM_IN_CART",
                    message=f"Cart {cart_id!r} contains restricted product {pid!r}",
                    collection="carts",
                    entity_id=cart_id,
                ))
    return issues
