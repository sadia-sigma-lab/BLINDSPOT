"""Finance domain-specific schemas extending shared models."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import ConfigDict, Field
from blindspot.data_model.resource import ResourceRecord


class FinanceAccountRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    account_number: str
    account_type: Literal["checking", "savings", "investment"]
    balance_usd: float = 0.0
    currency: str = "USD"
    authorized_users: list[str] = Field(default_factory=list)
    spending_limit_usd: float | None = None


class PaymentRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    payment_id: str
    amount_usd: float
    sender_account_id: str
    recipient_account_id: str
    recipient_external: bool = False
    status: Literal["draft", "pending_approval", "approved", "executed", "rejected", "cancelled"]
    purpose: str
    requires_dual_approval: bool = False
    approved_by: list[str] = Field(default_factory=list)


class PIIRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    subject_id: str
    pii_type: Literal["name", "address", "ssn_hash", "bank_details", "dob"]
    value: str  # always masked/tokenised
    redacted: bool = True
    access_log: list[str] = Field(default_factory=list)
