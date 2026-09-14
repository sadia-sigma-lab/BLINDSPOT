"""E-commerce domain-specific schemas extending shared models."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import ConfigDict, Field
from blindspot.data_model.resource import ResourceRecord


class ProductRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    # entity_id doubles as product_id
    name: str
    category: str
    price_usd: float
    description: str = ""
    brand: str = ""
    in_stock: bool = True
    rating: float = 0.0
    review_count: int = 0


class CartRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    customer_id: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    total_usd: float = 0.0
    budget_limit: float = 1000.0


class EcomOrderRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    customer_id: str
    product_ids: list[str] = Field(default_factory=list)
    total_usd: float = 0.0
    status: Literal[
        "pending", "processing", "shipped", "delivered", "cancelled"
    ] = "pending"
    payment_verified: bool = False
