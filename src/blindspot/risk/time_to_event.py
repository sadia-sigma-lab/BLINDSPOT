"""Time-to-event label computation."""

from __future__ import annotations

from typing import Any


def compute_time_to_event(
    step: int,
    event_steps: list[int],
) -> int | None:
    """
    Return the minimum steps from `step` to the first future event.
    Returns None if no event occurs (censored or never).
    """
    future_events = [es - step for es in sorted(event_steps) if es > step]
    return future_events[0] if future_events else None


def compute_all_tte(
    step: int,
    event_steps_by_target: dict[str, list[int]],
) -> dict[str, int | None]:
    """Return TTE for each event target at a given step."""
    return {
        target: compute_time_to_event(step, event_steps)
        for target, event_steps in event_steps_by_target.items()
    }
