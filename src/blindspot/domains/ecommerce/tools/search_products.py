"""search-products tool for e-commerce domain."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict
from blindspot.core.identifiers import ComponentID
from blindspot.tools.base import PythonTool
from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView


class SearchProductsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    category: str | None = None
    max_price: float | None = None


class SearchProductsTool(PythonTool[SearchProductsArgs, BaseModel]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="search-products", version="1.0.0"),
        display_name="Search Products",
        description="Search for products by name/description, optionally filtered by category or price.",
        read_scopes=["products", "resources"],
        write_scopes=[],
        side_effect_level="none",
        idempotent=True,
    )
    args_model = SearchProductsArgs
    output_model = BaseModel

    def read(self, view: ReadOnlyStateView, args: SearchProductsArgs, context: ToolExecutionContext) -> Any:
        products = view.get_collection("products") if view.has_scope("products") else {}
        query_lower = args.query.lower()
        results = []
        for pid, product in products.items():
            if not isinstance(product, dict):
                continue
            # Skip restricted items from search results
            if product.get("classification") == "restricted":
                continue
            # Filter by query (name or description match)
            name = (product.get("name") or "").lower()
            description = (product.get("description") or "").lower()
            if query_lower not in name and query_lower not in description:
                continue
            # Filter by category
            if args.category and product.get("category") != args.category:
                continue
            # Filter by max_price
            price = product.get("price_usd", 0.0) or 0.0
            if args.max_price is not None and price > args.max_price:
                continue
            results.append({
                "product_id": pid,
                "name": product.get("name"),
                "category": product.get("category"),
                "price_usd": price,
                "in_stock": product.get("in_stock", False),
                "rating": product.get("rating", 0.0),
                "brand": product.get("brand", ""),
            })
        return {"products": results, "count": len(results)}

    def plan_mutations(self, view: ReadOnlyStateView, args: SearchProductsArgs, context: ToolExecutionContext) -> MutationPlan:
        return MutationPlan()
