"""Deterministic event emitter for tool-triggered environment events."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from blindspot.core.event import EnvironmentEvent

if TYPE_CHECKING:
    from blindspot.runtime.event_queue import EventQueue
    from blindspot.tools.context import ToolExecutionContext


class EventEmitter:
    """Enqueues events produced by tool executions."""

    def __init__(self, event_queue: "EventQueue") -> None:
        self._queue = event_queue

    def emit(
        self,
        events: list[EnvironmentEvent],
        *,
        context: "ToolExecutionContext",
    ) -> list[str]:
        """Enqueue events; return their IDs in deterministic order."""
        ids: list[str] = []
        for event in events:
            # Tag source tool in payload
            enriched_payload = dict(event.payload)
            enriched_payload.setdefault("source_tool_call_id", context.tool_call_id)
            enriched_payload.setdefault("source_actor_id", context.actor_id)

            enriched = EnvironmentEvent(
                event_id=event.event_id,
                event_type=event.event_type,
                trigger_step=event.trigger_step,
                trigger_condition=event.trigger_condition,
                payload=enriched_payload,
                visible_to_agent=event.visible_to_agent,
                processed=False,
            )
            self._queue.enqueue(enriched)
            ids.append(enriched.event_id)
        return ids
