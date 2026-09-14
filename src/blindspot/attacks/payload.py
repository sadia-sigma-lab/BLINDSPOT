"""Attack payload contract."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AttackPayload(BaseModel):
    """A single adversarial payload unit."""

    model_config = ConfigDict(frozen=True)

    payload_id: str
    payload_type: Literal[
        "message",
        "document_content",
        "tool_output",
        "memory_record",
        "event_payload",
        "metadata",
        "user_instruction",
    ]
    content: Any
    source_id: str
    trust_label: str | None = None
    provenance_ids: list[str] = Field(default_factory=list)
    verifier_labels: dict[str, Any] = Field(default_factory=dict)

    def agent_visible_content(self) -> Any:
        """Return content with verifier labels stripped."""
        if isinstance(self.content, dict):
            cleaned = {k: v for k, v in self.content.items() if not k.startswith("__")}
            return cleaned
        return self.content


class ScheduledPayload(BaseModel):
    """A payload scheduled for delivery at a specific step or hook."""

    model_config = ConfigDict(frozen=True)

    payload: AttackPayload
    trigger_step: int | None = None
    trigger_hook: str | None = None
    trigger_condition: dict[str, Any] | None = None
    delivered: bool = False
    delivery_step: int | None = None
