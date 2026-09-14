"""Environment event contract."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class EnvironmentEvent(BaseModel):
    """An event that can be queued and processed by the runtime engine."""

    model_config = ConfigDict(frozen=False)

    event_id: str
    event_type: str
    trigger_step: int | None = None
    trigger_condition: dict[str, Any] | None = None
    payload: dict[str, Any]
    visible_to_agent: bool = False
    processed: bool = False
