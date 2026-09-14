"""Clean control generation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from blindspot.attacks.config import AttackConfig
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.state import AttackState


class CleanControlSpec(BaseModel):
    """Specification for deriving a clean control from an adversarial attack."""

    model_config = ConfigDict(frozen=True)

    control_id: str
    source_attack_id: str
    transformation: Literal[
        "remove_payload",
        "benign_payload",
        "trusted_source",
        "safe_target",
        "no_activation",
    ]
    parameters: dict[str, Any] = Field(default_factory=dict)


class BenignControlAttack:
    """No-op attack that validates lifecycle plumbing without adversarial content."""

    from blindspot.attacks.metadata import AttackMetadata
    from blindspot.attacks.taxonomy import (
        AttackSource, AttackTarget, AttackTemporalPattern,
        AttackHarmCategory, AttackerKnowledgeTier,
    )
    from blindspot.core.identifiers import ComponentID

    metadata = AttackMetadata(
        attack_id=ComponentID(namespace="core", name="benign-control", version="1.0.0"),
        display_name="Benign Control",
        description="No adversarial effect. Validates lifecycle plumbing.",
        family="control",
        source=AttackSource.ENVIRONMENT,
        targets=[],
        mechanisms=[],
        temporal_patterns=[AttackTemporalPattern.ONE_SHOT],
        harm_categories=[],
        knowledge_tier=AttackerKnowledgeTier.STATIC,
        required_hooks=["after_observation"],
        supports_adaptation=False,
        deterministic=True,
    )

    def initialize(self, config, scenario, context) -> AttackState:
        return AttackState(
            attack_instance_id=f"benign-{context.step}",
            attack_id="core:benign-control@1.0.0",
            scenario_id=context.scenario_id,
            active=True,
            current_session=context.session_id,
        )

    def on_hook(self, hook, state, context):
        return state, AttackEffect.noop()

    def evaluate_progress(self, state, world_state, trajectory):
        from blindspot.attacks.progress import AttackProgressResult
        return AttackProgressResult(
            progress=0.0, achieved_nodes=[], newly_achieved_nodes=[],
            blocked_nodes=[], terminal_nodes_achieved=[],
        )

    def evaluate_success(self, state, world_state, trajectory):
        from blindspot.attacks.predicates import AttackPredicateResult
        return AttackPredicateResult(satisfied=False, predicate_id="noop_control")
