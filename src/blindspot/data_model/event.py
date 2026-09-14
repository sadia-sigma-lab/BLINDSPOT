"""Scheduled event record model."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.base import BaseEntity


class ScheduledEventRecord(BaseEntity):
    """An event that fires at a step, simulated time, or condition."""

    model_config = ConfigDict(frozen=False)  # mutable: processed flag is toggled

    event_type: str
    trigger_step: int | None = None
    trigger_time: datetime | None = None
    trigger_condition: dict[str, Any] | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    visibility: Literal["public", "private", "hidden"] = "private"
    processed: bool = False
