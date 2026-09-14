"""Deterministic simulated clock for benchmark episodes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, field_validator


class SimulatedClock(BaseModel):
    """Advances time by a fixed interval per step — no wall-clock dependency."""

    model_config = ConfigDict(frozen=False)

    current_time: datetime
    step_duration_seconds: int = 60

    @field_validator("current_time")
    @classmethod
    def _require_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("current_time must be timezone-aware")
        return v

    def advance(self, steps: int = 1) -> datetime:
        """Advance the clock by the given number of steps and return the new time."""
        self.current_time = self.current_time + timedelta(
            seconds=self.step_duration_seconds * steps
        )
        return self.current_time

    @classmethod
    def from_iso(cls, iso_string: str, step_duration_seconds: int = 60) -> "SimulatedClock":
        """Construct from an ISO-8601 datetime string."""
        dt = datetime.fromisoformat(iso_string)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(current_time=dt, step_duration_seconds=step_duration_seconds)
