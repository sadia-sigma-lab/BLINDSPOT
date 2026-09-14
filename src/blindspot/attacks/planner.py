"""Attack planner abstraction — deterministic rule-based baseline."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.context import AttackContext
from blindspot.attacks.metadata import AttackMetadata
from blindspot.attacks.state import AttackState


class AttackPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    plan_id: str
    phases: list[str]
    target_nodes: list[str]
    payload_templates: list[str]
    stopping_conditions: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackPlanner(ABC):
    """Abstract planner interface — supports future LLM-backed planners."""

    @abstractmethod
    def create_plan(
        self,
        attack: AttackMetadata,
        scenario: Any,
        context: AttackContext,
    ) -> AttackPlan:
        ...

    @abstractmethod
    def revise_plan(
        self,
        plan: AttackPlan,
        state: AttackState,
        context: AttackContext,
    ) -> AttackPlan:
        ...


class RuleBasedPlanner(AttackPlanner):
    """Deterministic rule-based planner that follows a fixed phase sequence."""

    def __init__(self, phases: list[str], target_nodes: list[str]) -> None:
        self._phases = phases
        self._target_nodes = target_nodes

    def create_plan(self, attack, scenario, context) -> AttackPlan:
        import hashlib
        plan_id = hashlib.sha256(
            f"{attack.attack_id.canonical()}:{context.seed}:{context.step}".encode()
        ).hexdigest()[:12]
        return AttackPlan(
            plan_id=plan_id,
            phases=list(self._phases),
            target_nodes=list(self._target_nodes),
            payload_templates=[],
            stopping_conditions=["success_achieved", "budget_exhausted"],
            metadata={"planner": "rule_based"},
        )

    def revise_plan(self, plan, state, context) -> AttackPlan:
        # Rule-based planner does not revise
        return plan
