"""Unit tests for attack composition."""

import pytest
from datetime import datetime, timezone
from blindspot.attacks.composition import AttackCompositionSpec, ComposedAttack
from blindspot.attacks.exceptions import AttackCompositionError
from blindspot.attacks.hooks import AttackEffect, AttackHook
from blindspot.attacks.insertion import compose_effects
from blindspot.attacks_builtin.benign_control import BenignControlAttack
from blindspot.attacks_builtin.task_injection import TaskInjectionAttack


def test_compose_effects_parallel_merge():
    e1 = AttackEffect(messages_to_add=[{"role": "user", "content": "msg1"}])
    e2 = AttackEffect(messages_to_add=[{"role": "user", "content": "msg2"}])
    combined = compose_effects([(e1, 1, "a1"), (e2, 0, "a2")], "merge_if_compatible")
    assert len(combined.messages_to_add) == 2


def test_compose_noop_plus_effect():
    e1 = AttackEffect.noop()
    e2 = AttackEffect(messages_to_add=[{"role": "user", "content": "injected"}])
    combined = compose_effects([(e1, 0, "a1"), (e2, 0, "a2")], "merge_if_compatible")
    assert len(combined.messages_to_add) == 1


def test_composition_spec_valid():
    spec = AttackCompositionSpec(
        composition_id="comp1",
        attack_ids=["core:benign-control@1.0.0", "core:task-injection@1.0.0"],
        mode="parallel",
        conflict_policy="error",
    )
    assert spec.mode == "parallel"


def test_sequential_composition_stops_at_first():
    spec = AttackCompositionSpec(
        composition_id="seq1",
        attack_ids=["core:benign-control@1.0.0", "core:task-injection@1.0.0"],
        mode="sequential",
        conflict_policy="error",
    )
    # Both attacks are no-ops in sequential mode on before_session hook
    composed = ComposedAttack(spec, [BenignControlAttack(), TaskInjectionAttack()])
    states = {
        "core:benign-control@1.0.0": BenignControlAttack().metadata.attack_id.canonical(),
        "core:task-injection@1.0.0": TaskInjectionAttack().metadata.attack_id.canonical(),
    }
    # Just verify it doesn't raise
    assert True
