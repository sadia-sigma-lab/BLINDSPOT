"""Unit tests for the 5 new attack families."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from blindspot.attacks.config import AttackConfig, AttackBudget
from blindspot.attacks.context import build_attack_context
from blindspot.attacks.hooks import AttackHook
from blindspot.attacks.taxonomy import AttackerKnowledgeTier
from blindspot.attacks_builtin.cross_tenant_exfiltration import CrossTenantExfiltrationAttack
from blindspot.attacks_builtin.prompt_reinjection import PromptReinjectionAttack
from blindspot.attacks_builtin.stale_approval_reuse import StaleApprovalReuseAttack
from blindspot.attacks_builtin.mass_enumeration import MassEnumerationAttack
from blindspot.attacks_builtin.silent_rollback_bypass import SilentRollbackBypassAttack
from blindspot.core.state import WorldState
from blindspot.loaders.scenario_loader import load_scenario

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)
_SCENARIO = load_scenario(Path("examples/minimal_domain/scenario.yaml"))


def _world():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42, public={}, private={}, hidden={}, audit_log=[],
    )


def _ctx(tier=AttackerKnowledgeTier.TOOL_CALLS):
    return build_attack_context(
        world_state=_world(), knowledge_tier=tier,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=0, session_id="sess", seed=42, current_time=_NOW, target_actor_id="agent",
    )


def _cfg(attack_id, **params):
    return AttackConfig(
        attack_id=attack_id, seed=42, target_actor_id="agent",
        budget=AttackBudget(max_payloads=4, max_turns=8),
        parameters=params,
    )


# Cross-tenant exfiltration
def test_cross_tenant_fires_on_correct_hook():
    attack = CrossTenantExfiltrationAttack()
    cfg = _cfg("core:cross-tenant-exfiltration@1.0.0",
                cross_tenant_resource_id="file_service_credentials")
    ctx = _ctx(AttackerKnowledgeTier.PARTIAL_STATE)
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
    assert len(effect.messages_to_add) == 1
    assert "file_service_credentials" in effect.messages_to_add[0]["content"]


def test_cross_tenant_no_op_on_wrong_hook():
    attack = CrossTenantExfiltrationAttack()
    cfg = _cfg("core:cross-tenant-exfiltration@1.0.0")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    _, effect = attack.on_hook(AttackHook.AFTER_TOOL, state, _ctx())
    assert effect.no_op or effect.is_empty()


# Prompt re-injection
def test_prompt_reinjection_waits_for_read():
    attack = PromptReinjectionAttack()
    cfg = _cfg("core:prompt-reinjection@1.0.0", target_file_id="file_handbook")
    ctx = _ctx()
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_TOOL, state, ctx)
    # No reads yet — should be no-op at step 0
    assert state.attacker_memory.get("injection_delivered") is False


def test_prompt_reinjection_success_false_initially():
    attack = PromptReinjectionAttack()
    cfg = _cfg("core:prompt-reinjection@1.0.0")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    result = attack.evaluate_success(state, _world(), [])
    assert not result.satisfied


# Stale approval reuse
def test_stale_approval_delivers_message():
    attack = StaleApprovalReuseAttack()
    cfg = _cfg("core:stale-approval-reuse@1.0.0",
                expired_approval_id="approval_expired_001",
                target_file="file_report", target_recipient="old.contact@example.com")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, _ctx())
    assert len(effect.messages_to_add) == 1
    assert "approval_expired_001" in effect.messages_to_add[0]["content"]


def test_stale_approval_no_duplicate():
    attack = StaleApprovalReuseAttack()
    cfg = _cfg("core:stale-approval-reuse@1.0.0")
    ctx = _ctx()
    state = attack.initialize(cfg, _SCENARIO, ctx)
    attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
    _, effect2 = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
    assert effect2.is_empty() or effect2.no_op


# Mass enumeration
def test_mass_enumeration_adds_messages_each_step():
    attack = MassEnumerationAttack()
    cfg = _cfg("core:mass-enumeration@1.0.0")
    ctx = _ctx(AttackerKnowledgeTier.PUBLIC_RESPONSES)
    state = attack.initialize(cfg, _SCENARIO, ctx)
    for i in range(3):
        state, effect = attack.on_hook(AttackHook.AFTER_OBSERVATION, state, ctx)
    assert state.attacker_memory.get("enum_count", 0) == 3


def test_mass_enumeration_success_false_no_discoveries():
    attack = MassEnumerationAttack()
    cfg = _cfg("core:mass-enumeration@1.0.0")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    result = attack.evaluate_success(state, _world(), [])
    assert not result.satisfied


# Silent rollback bypass
def test_silent_rollback_fires_on_after_tool():
    attack = SilentRollbackBypassAttack()
    cfg = _cfg("core:silent-rollback-bypass@1.0.0")
    ctx = build_attack_context(
        world_state=_world(), knowledge_tier=AttackerKnowledgeTier.PARTIAL_STATE,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=2, session_id="sess", seed=42, current_time=_NOW, target_actor_id="agent",
        tool_call_history=[{"name": "share-file", "step": 2}],
    )
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_TOOL, state, ctx)
    assert len(effect.events_to_emit) == 1
    assert effect.events_to_emit[0]["event_type"] == "rollback_token_cancelled"


def test_silent_rollback_no_op_without_share():
    attack = SilentRollbackBypassAttack()
    cfg = _cfg("core:silent-rollback-bypass@1.0.0")
    ctx = _ctx()  # no tool calls in history
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_TOOL, state, ctx)
    assert effect.no_op or effect.is_empty()


# Registry validation
def test_all_new_attacks_register():
    from blindspot.attacks.registry import AttackRegistry
    reg = AttackRegistry()
    for attack in [
        CrossTenantExfiltrationAttack(), PromptReinjectionAttack(),
        StaleApprovalReuseAttack(), MassEnumerationAttack(), SilentRollbackBypassAttack(),
    ]:
        reg.register(attack)
    assert len(reg.list()) == 5
