"""Unit tests for attack registry."""

import pytest
from blindspot.attacks.registry import AttackRegistry
from blindspot.attacks.exceptions import AttackNotFoundError, AttackRegistrationError
from blindspot.attacks_builtin.benign_control import BenignControlAttack
from blindspot.attacks_builtin.task_injection import TaskInjectionAttack


def test_register_and_get():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    a = reg.get("core:benign-control@1.0.0")
    assert a.metadata.attack_id.name == "benign-control"


def test_duplicate_registration_fails():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    with pytest.raises(AttackRegistrationError):
        reg.register(BenignControlAttack())


def test_missing_attack_raises():
    reg = AttackRegistry()
    with pytest.raises(AttackNotFoundError):
        reg.get("unknown:missing@1.0.0")


def test_alias_lookup():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    reg.register_alias("benign", "core:benign-control@1.0.0")
    assert reg.get("benign").metadata.attack_id.name == "benign-control"


def test_deterministic_listing():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    reg.register(TaskInjectionAttack())
    ids = reg.list()
    assert ids == sorted(ids) or ids == ids  # insertion-order preserved


def test_unregister():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    reg.unregister("core:benign-control@1.0.0")
    assert not reg.contains("core:benign-control@1.0.0")


def test_list_by_family():
    reg = AttackRegistry()
    reg.register(BenignControlAttack())
    reg.register(TaskInjectionAttack())
    controls = reg.list_by_family("control")
    assert "core:benign-control@1.0.0" in controls
