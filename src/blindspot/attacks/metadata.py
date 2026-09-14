"""Attack metadata contract."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from blindspot.attacks.taxonomy import (
    AttackHarmCategory, AttackMechanism, AttackSource, AttackTarget,
    AttackTemporalPattern, AttackerKnowledgeTier, KNOWN_HOOKS,
)
from blindspot.core.identifiers import ComponentID


class AttackMetadata(BaseModel):
    """Declarative metadata for a registered benchmark attack."""

    model_config = ConfigDict(frozen=True)

    attack_id: ComponentID
    display_name: str
    description: str
    family: str
    source: AttackSource
    targets: list[AttackTarget]
    mechanisms: list[str]
    temporal_patterns: list[AttackTemporalPattern]
    harm_categories: list[str]
    knowledge_tier: AttackerKnowledgeTier
    supported_domains: list[str] = Field(default_factory=list)
    required_hooks: list[str] = Field(default_factory=list)
    supports_adaptation: bool = False
    supports_composition: bool = True
    supports_multi_session: bool = False
    deterministic: bool = True
    tags: list[str] = Field(default_factory=list)
    deprecated: bool = False
    license: str = "Apache-2.0"
    source_package: str = ""
    threat_model_notes: str = ""

    @model_validator(mode="after")
    def _validate_consistency(self) -> "AttackMetadata":
        for hook in self.required_hooks:
            if hook not in KNOWN_HOOKS:
                raise ValueError(f"Unknown hook {hook!r}; known hooks: {sorted(KNOWN_HOOKS)}")

        for pattern in self.temporal_patterns:
            if pattern == AttackTemporalPattern.ADAPTIVE and not self.supports_adaptation:
                raise ValueError(
                    "Attack has adaptive temporal pattern but supports_adaptation=False"
                )
            if pattern == AttackTemporalPattern.CROSS_SESSION and not self.supports_multi_session:
                raise ValueError(
                    "Attack has cross_session pattern but supports_multi_session=False"
                )

        if (
            self.knowledge_tier == AttackerKnowledgeTier.INTERNAL_REASONING
            and not self.threat_model_notes
        ):
            raise ValueError(
                "knowledge_tier=internal_reasoning requires a threat_model_notes declaration"
            )

        return self
