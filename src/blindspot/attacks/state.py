"""Attack instance state — verifier-visible, not exposed to target agent."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AttackState(BaseModel):
    """Mutable tracking state for one running attack instance."""

    model_config = ConfigDict(frozen=False)

    attack_instance_id: str
    attack_id: str
    scenario_id: str
    active: bool = False
    completed: bool = False
    succeeded: bool = False
    aborted: bool = False
    abort_reason: str | None = None
    current_phase: str = "initialized"
    current_step: int = 0
    current_session: str = ""
    payload_count: int = 0
    optimization_steps: int = 0
    progress: float = 0.0
    achieved_nodes: list[str] = Field(default_factory=list)
    pending_nodes: list[str] = Field(default_factory=list)
    attacker_memory: dict[str, Any] = Field(default_factory=dict)
    verifier_only: dict[str, Any] = Field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot (excludes verifier_only)."""
        d = self.model_dump()
        d.pop("verifier_only", None)
        return d

    def is_terminal(self) -> bool:
        return self.completed or self.succeeded or self.aborted
