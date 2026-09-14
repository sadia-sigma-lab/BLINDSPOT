"""Customer service domain-specific schemas extending shared models."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import ConfigDict, Field
from blindspot.data_model.resource import ResourceRecord


class CustomerAccount(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    account_number: str  # masked, e.g. "****1001"
    email: str
    phone: str = ""
    status: Literal["active", "suspended", "closed"] = "active"
    order_ids: list[str] = Field(default_factory=list)
    loyalty_tier: Literal["standard", "silver", "gold"] = "standard"
    attributes: dict[str, Any] = Field(default_factory=dict)


class OrderRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    # entity_id doubles as order_id
    customer_id: str
    product_ids: list[str] = Field(default_factory=list)
    total_usd: float
    status: Literal[
        "pending", "processing", "shipped", "delivered", "cancelled", "refunded"
    ] = "pending"
    eligible_for_refund: bool = False
    refund_amount: float = 0.0


class SupportTicket(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    # entity_id doubles as ticket_id
    customer_id: str
    subject: str
    description: str = ""
    status: Literal["open", "in_progress", "resolved", "closed"] = "open"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    assigned_to: str | None = None
    resolution: str | None = None
