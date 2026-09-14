"""Message record model."""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class MessageRecord(BaseEntity):
    """A communication artifact between actors in the domain."""

    model_config = ConfigDict(frozen=True)

    sender_id: str
    recipient_ids: list[str]
    subject: str
    body: str
    attachment_ids: list[str] = Field(default_factory=list)
    trust_level: Literal["trusted", "internal", "external", "unknown"]
    channel: str
    thread_id: str | None = None
    visible_to: list[str] = Field(default_factory=list)
