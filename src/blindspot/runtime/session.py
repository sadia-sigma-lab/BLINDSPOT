"""Runtime session — wraps state, event queue, and step counter."""

from __future__ import annotations

import hashlib
import json
import random
import uuid
from typing import Any

from blindspot.core.scenario import ScenarioSpec
from blindspot.core.state import WorldState
from blindspot.runtime.event_queue import EventQueue


def _hash_state(state: WorldState) -> str:
    """Return a stable SHA-256 hash of the state's public and private fields."""
    payload = json.dumps(
        {"public": state.public, "private": state.private},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class Session:
    """Holds mutable runtime state for a single episode."""

    def __init__(
        self,
        scenario: ScenarioSpec,
        initial_state: WorldState,
        seed: int,
        episode_id: str | None = None,
    ) -> None:
        self.scenario = scenario
        self.state = initial_state
        self.seed = seed
        self.episode_id = episode_id or str(uuid.uuid4())
        self.session_id = initial_state.session_id
        self.step = 0
        self.event_queue = EventQueue()
        self.rng = random.Random(seed)
        self._terminated = False
        self._truncated = False

        # Enqueue scenario events
        from blindspot.core.event import EnvironmentEvent

        for ev in scenario.events:
            self.event_queue.enqueue(EnvironmentEvent(**ev))

    @property
    def current_state_hash(self) -> str:
        return _hash_state(self.state)

    @property
    def max_steps(self) -> int:
        return self.scenario.horizon.get("max_steps", 20)

    @property
    def terminated(self) -> bool:
        return self._terminated

    @property
    def truncated(self) -> bool:
        return self._truncated

    def terminate(self) -> None:
        self._terminated = True

    def truncate(self) -> None:
        self._truncated = True

    def rng_state_dict(self) -> dict[str, Any]:
        state = self.rng.getstate()
        return {"version": state[0], "internalstate": list(state[1]), "gauss_next": state[2]}

    def restore_rng_state(self, state_dict: dict[str, Any]) -> None:
        tup = (
            state_dict["version"],
            tuple(state_dict["internalstate"]),
            state_dict["gauss_next"],
        )
        self.rng.setstate(tup)  # type: ignore[arg-type]
