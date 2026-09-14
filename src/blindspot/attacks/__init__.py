"""Attack subsystem — modular, compositional, domain-agnostic."""

from blindspot.attacks.taxonomy import (
    AttackSource, AttackTarget, AttackMechanism,
    AttackTemporalPattern, AttackHarmCategory, AttackerKnowledgeTier,
)
from blindspot.attacks.metadata import AttackMetadata
from blindspot.attacks.config import AttackConfig, AttackBudget
from blindspot.attacks.state import AttackState
from blindspot.attacks.registry import AttackRegistry

__all__ = [
    "AttackSource", "AttackTarget", "AttackMechanism",
    "AttackTemporalPattern", "AttackHarmCategory", "AttackerKnowledgeTier",
    "AttackMetadata", "AttackConfig", "AttackBudget",
    "AttackState", "AttackRegistry",
]
