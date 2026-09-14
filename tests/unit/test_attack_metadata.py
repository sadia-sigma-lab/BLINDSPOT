"""Unit tests for attack metadata validation."""

import pytest
from blindspot.attacks.metadata import AttackMetadata
from blindspot.attacks.taxonomy import (
    AttackSource, AttackTarget, AttackTemporalPattern,
    AttackHarmCategory, AttackerKnowledgeTier,
)
from blindspot.core.identifiers import ComponentID


def _cid(name: str) -> ComponentID:
    return ComponentID(namespace="core", name=name, version="1.0.0")


def _base(**kwargs):
    defaults = dict(
        attack_id=_cid("test-attack"),
        display_name="Test", description="d",
        family="test",
        source=AttackSource.ENVIRONMENT,
        targets=[AttackTarget.INTENT],
        mechanisms=["indirect_injection"],
        temporal_patterns=[AttackTemporalPattern.ONE_SHOT],
        harm_categories=["confidentiality"],
        knowledge_tier=AttackerKnowledgeTier.STATIC,
    )
    defaults.update(kwargs)
    return defaults


def test_valid_attack_metadata():
    m = AttackMetadata(**_base())
    assert m.attack_id.name == "test-attack"


def test_adaptive_without_support_fails():
    with pytest.raises(Exception):
        AttackMetadata(**_base(
            temporal_patterns=[AttackTemporalPattern.ADAPTIVE],
            supports_adaptation=False,
        ))


def test_cross_session_without_support_fails():
    with pytest.raises(Exception):
        AttackMetadata(**_base(
            temporal_patterns=[AttackTemporalPattern.CROSS_SESSION],
            supports_multi_session=False,
        ))


def test_unknown_hook_fails():
    with pytest.raises(Exception):
        AttackMetadata(**_base(required_hooks=["nonexistent_hook"]))


def test_internal_reasoning_without_threat_model_fails():
    with pytest.raises(Exception):
        AttackMetadata(**_base(
            knowledge_tier=AttackerKnowledgeTier.INTERNAL_REASONING,
            threat_model_notes="",
        ))


def test_internal_reasoning_with_threat_model_passes():
    m = AttackMetadata(**_base(
        knowledge_tier=AttackerKnowledgeTier.INTERNAL_REASONING,
        threat_model_notes="Requires compromise of reasoning infrastructure.",
    ))
    assert m.knowledge_tier == AttackerKnowledgeTier.INTERNAL_REASONING
