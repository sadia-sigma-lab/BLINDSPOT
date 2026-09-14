"""Unit tests for event emission."""

import uuid
from blindspot.core.event import EnvironmentEvent
from blindspot.runtime.event_queue import EventQueue
from blindspot.tools.events import EventEmitter
from blindspot.tools.runtime import make_context


def _event(visible: bool = False) -> EnvironmentEvent:
    return EnvironmentEvent(
        event_id=str(uuid.uuid4()), event_type="test_event",
        trigger_step=5, payload={"data": "x"}, visible_to_agent=visible,
    )


def test_events_enqueued():
    q = EventQueue()
    emitter = EventEmitter(q)
    ctx = make_context("user_alice", step=0, seed=42)
    ids = emitter.emit([_event(), _event()], context=ctx)
    assert len(ids) == 2
    assert len(q) == 2


def test_source_tagged_in_payload():
    q = EventQueue()
    emitter = EventEmitter(q)
    ctx = make_context("user_alice", step=2, seed=42, tool_call_id="call-123")
    emitter.emit([_event()], context=ctx)
    due = q.due_events(5)
    assert due[0].payload["source_tool_call_id"] == "call-123"
    assert due[0].payload["source_actor_id"] == "user_alice"
