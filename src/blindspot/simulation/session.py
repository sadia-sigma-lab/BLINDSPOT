"""Multi-session execution manager."""

from __future__ import annotations

import uuid
from typing import Any

from blindspot.core.state import WorldState
from blindspot.simulation.context import SessionState, SimulationContext


class SessionManager:
    """Manages session transitions with persistent world state."""

    def __init__(self) -> None:
        self._sessions: list[SessionState] = []
        self._current: SessionState | None = None

    def start_session(
        self,
        context: SimulationContext,
        active_actor_ids: list[str],
        previous_history: bool = False,
    ) -> SessionState:
        session = SessionState(
            session_id=context.session_id,
            session_index=len(self._sessions),
            started_at_step=context.global_step,
            active_actor_ids=active_actor_ids,
        )
        self._sessions.append(session)
        self._current = session
        return session

    def end_session(self, context: SimulationContext) -> None:
        if self._current:
            self._current.ended_at_step = context.global_step

    def transition(
        self,
        world_state: WorldState,
        new_session_id: str | None = None,
        reason: str = "horizon_reached",
    ) -> tuple[str, dict[str, Any]]:
        """Create a new session while preserving world state. Return (new_session_id, metadata)."""
        sid = new_session_id or str(uuid.uuid4())
        return sid, {
            "transition_reason": reason,
            "previous_session": self._current.session_id if self._current else None,
            "world_state_preserved": True,
        }

    @property
    def current(self) -> SessionState | None:
        return self._current

    def all_sessions(self) -> list[SessionState]:
        return list(self._sessions)
