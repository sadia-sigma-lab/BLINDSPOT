"""Unit tests for attack hooks and effects."""

import pytest
from blindspot.attacks.hooks import AttackEffect, AttackHook


def test_noop_effect_valid():
    e = AttackEffect.noop()
    assert e.no_op
    assert e.is_empty()


def test_effect_with_message_not_empty():
    e = AttackEffect(messages_to_add=[{"role": "user", "content": "injected"}])
    assert not e.is_empty()


def test_invalid_effect_detected():
    e = AttackEffect(messages_to_add=[{"role": "user"}])  # missing content
    errors = e.validate_effect()
    assert len(errors) > 0


def test_valid_effect_no_errors():
    e = AttackEffect(messages_to_add=[{"role": "user", "content": "hello"}])
    errors = e.validate_effect()
    assert errors == []


def test_hook_enum_values():
    assert AttackHook.AFTER_OBSERVATION.value == "after_observation"
    assert AttackHook.ON_EPISODE_END.value == "on_episode_end"
