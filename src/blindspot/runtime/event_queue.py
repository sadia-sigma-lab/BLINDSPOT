"""Deterministic event queue for the runtime engine."""

from __future__ import annotations

from collections import deque
from typing import Any

from blindspot.core.event import EnvironmentEvent


class EventQueue:
    """FIFO queue of EnvironmentEvents with step-based trigger filtering."""

    def __init__(self) -> None:
        self._queue: deque[EnvironmentEvent] = deque()

    def enqueue(self, event: EnvironmentEvent) -> None:
        self._queue.append(event)

    def due_events(self, current_step: int) -> list[EnvironmentEvent]:
        """Return events that should fire at or before current_step."""
        due = []
        remaining: deque[EnvironmentEvent] = deque()
        for event in self._queue:
            if event.processed:
                continue
            if event.trigger_step is None or event.trigger_step <= current_step:
                due.append(event)
            else:
                remaining.append(event)
        self._queue = remaining
        return due

    def mark_processed(self, event_id: str) -> None:
        for event in self._queue:
            if event.event_id == event_id:
                event.processed = True

    def to_list(self) -> list[dict[str, Any]]:
        return [e.model_dump() for e in self._queue]

    @classmethod
    def from_list(cls, records: list[dict[str, Any]]) -> "EventQueue":
        q = cls()
        for r in records:
            q.enqueue(EnvironmentEvent(**r))
        return q

    def __len__(self) -> int:
        return len(self._queue)
