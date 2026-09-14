"""add-to-cart tool for e-commerce domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class AddToCartArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: str
    quantity: int = 1


class AddToCartTool(PythonTool[AddToCartArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="add-to-cart", version="1.0.0"),
        display_name="Add to Cart",
        description="Add a product to the actor's shopping cart.",
        read_scopes=["products", "carts", "resources"],
        write_scopes=["carts", "resources"],
        side_effect_level="low",
    )
    args_model = AddToCartArgs
    output_model = BaseModel

    def _find_actor_cart(self, carts: dict, actor_id: str) -> tuple[str | None, dict | None]:
        for cart_id, cart in carts.items():
            if isinstance(cart, dict) and cart.get("customer_id") == actor_id:
                return cart_id, cart
        return None, None

    def read(self, view: ReadOnlyStateView, args: AddToCartArgs, context: ToolExecutionContext) -> Any:
        products = view.get_collection("products") if view.has_scope("products") else {}
        carts = view.get_collection("carts") if view.has_scope("carts") else {}

        product = products.get(args.product_id)
        if product is None:
            raise ValueError(f"Product {args.product_id!r} not found")
        if not isinstance(product, dict):
            raise ValueError(f"Product {args.product_id!r} has unexpected format")
        if product.get("classification") == "restricted":
            raise ValueError(f"Product {args.product_id!r} is restricted and cannot be added to cart")
        if not product.get("in_stock", False):
            raise ValueError(f"Product {args.product_id!r} is out of stock")

        cart_id, cart = self._find_actor_cart(carts, context.actor_id)
        if cart is None:
            raise ValueError(f"No cart found for actor {context.actor_id!r}")

        price = product.get("price_usd", 0.0) or 0.0
        new_total = (cart.get("total_usd", 0.0) or 0.0) + price * args.quantity
        budget = cart.get("budget_limit", float("inf")) or float("inf")
        if new_total > budget:
            raise ValueError(
                f"Adding {args.quantity}x {args.product_id!r} would exceed budget limit "
                f"({new_total:.2f} > {budget:.2f})"
            )
        return {
            "cart_id": cart_id,
            "product_id": args.product_id,
            "quantity": args.quantity,
            "item_price": price,
            "new_total": new_total,
        }

    def plan_mutations(self, view: ReadOnlyStateView, args: AddToCartArgs, context: ToolExecutionContext) -> MutationPlan:
        products = view.get_collection("products") if view.has_scope("products") else {}
        carts = view.get_collection("carts") if view.has_scope("carts") else {}

        product = products.get(args.product_id)
        if product is None or not isinstance(product, dict):
            return MutationPlan()
        if product.get("classification") == "restricted" or not product.get("in_stock", False):
            return MutationPlan()

        cart_id, cart = self._find_actor_cart(carts, context.actor_id)
        if cart is None or cart_id is None:
            return MutationPlan()

        price = product.get("price_usd", 0.0) or 0.0
        new_total = (cart.get("total_usd", 0.0) or 0.0) + price * args.quantity
        budget = cart.get("budget_limit", float("inf")) or float("inf")
        if new_total > budget:
            return MutationPlan()

        # Update items list
        existing_items = list(cart.get("items", []))
        # Check if product already in cart — update quantity
        found = False
        for i, item in enumerate(existing_items):
            if isinstance(item, dict) and item.get("product_id") == args.product_id:
                existing_items[i] = {**item, "quantity": item.get("quantity", 0) + args.quantity}
                found = True
                break
        if not found:
            existing_items.append({"product_id": args.product_id, "quantity": args.quantity, "price_usd": price})

        updated = {**cart, "items": existing_items, "total_usd": new_total}
        return MutationPlan(operations=[MutationOperation(
            collection="carts",
            entity_id=cart_id,
            operation="update",
            before=dict(cart),
            after=updated,
            changed_fields=["items", "total_usd"],
        )])
