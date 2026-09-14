"""Deterministic tool failure model."""

from __future__ import annotations

import random
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from blindspot.tools.errors import ToolError


class ToolFailureProfile(BaseModel):
    """Deterministic failure configuration for a tool or tool set."""

    model_config = ConfigDict(frozen=True)

    profile_id: str
    enabled: bool = True
    failure_probability: float = 0.0
    failure_stage: Literal[
        "before_authorization",
        "before_execution",
        "before_commit",
        "after_commit",
        "response_only",
    ]
    failure_type: Literal[
        "timeout",
        "transient_error",
        "permission_race",
        "stale_result",
        "false_success",
        "partial_observation",
        "malformed_output",
    ]
    applicable_tools: list[str] = Field(default_factory=list)
    seed_offset: int = 0
    parameters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("failure_probability")
    @classmethod
    def _valid_probability(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"failure_probability must be in [0,1], got {v}")
        return v


class ToolFailureModel:
    """Checks whether a failure should occur at a given stage under a fixed seed."""

    def __init__(self, profiles: list[ToolFailureProfile] | None = None) -> None:
        self._profiles = profiles or []

    def should_fail(
        self,
        tool_id: str,
        stage: str,
        seed: int,
        step: int,
    ) -> tuple[bool, ToolFailureProfile | None]:
        """Return (should_fail, matching_profile)."""
        for profile in self._profiles:
            if not profile.enabled:
                continue
            if profile.failure_stage != stage:
                continue
            if profile.applicable_tools and tool_id not in profile.applicable_tools:
                continue
            rng = random.Random(seed ^ (step * 31337) ^ profile.seed_offset)
            if rng.random() < profile.failure_probability:
                return True, profile
        return False, None

    def build_error(self, profile: ToolFailureProfile) -> ToolError:
        """Create an agent-visible error from a failure profile."""
        if profile.failure_type == "timeout":
            return ToolError.transient("Tool timed out")
        if profile.failure_type == "transient_error":
            return ToolError.transient("Transient error occurred")
        if profile.failure_type == "permission_race":
            return ToolError.authorization("Permission changed during execution")
        if profile.failure_type in ("stale_result", "partial_observation"):
            return ToolError(
                code="STALE_RESULT", category="transient",
                message="Result may be stale", retryable=True,
            )
        if profile.failure_type in ("false_success", "malformed_output"):
            return ToolError.internal("Output could not be serialized")
        return ToolError.internal("Simulated failure")

    @classmethod
    def null(cls) -> "ToolFailureModel":
        """No failures ever fire."""
        return cls([])
