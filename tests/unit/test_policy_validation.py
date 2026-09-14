"""Unit tests for policy validator."""

import pytest
from datetime import datetime, timezone

from blindspot.data_model.policy import PolicyDocument, PolicyRule
from blindspot.validators.policies import PolicyValidator

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _doc(**kwargs):
    base = dict(entity_id="pol1", schema_version="1.0.0", created_at=_NOW, updated_at=_NOW,
                title="Test", domain="test")
    base.update(kwargs)
    return PolicyDocument(**base)


def _bundle(docs):
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
    b = DomainStateBundle()
    b.policies = {d.entity_id: d for d in docs}
    return b


def test_valid_policy_no_issues():
    doc = _doc(rules=[
        PolicyRule(rule_id="r1", description="d", effect="allow", action_pattern="read")
    ])
    issues = PolicyValidator().validate(_bundle([doc]))
    assert not issues


def test_duplicate_rule_id_in_doc_rejected_at_model_level():
    with pytest.raises(Exception):
        _doc(rules=[
            PolicyRule(rule_id="r1", description="d", effect="allow", action_pattern="read"),
            PolicyRule(rule_id="r1", description="e", effect="deny", action_pattern="read"),
        ])


def test_empty_action_pattern_fails():
    doc = _doc(rules=[
        PolicyRule(rule_id="r1", description="d", effect="allow", action_pattern="")
    ])
    issues = PolicyValidator().validate(_bundle([doc]))
    assert any(i.code == "EMPTY_ACTION_PATTERN" for i in issues)
