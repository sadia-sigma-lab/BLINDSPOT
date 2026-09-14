"""Unit tests for Skill 14 attack families."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from blindspot.attacks.config import AttackConfig, AttackBudget
from blindspot.attacks.context import build_attack_context
from blindspot.attacks.hooks import AttackHook
from blindspot.attacks.taxonomy import AttackerKnowledgeTier
from blindspot.core.state import WorldState
from blindspot.loaders.scenario_loader import load_scenario

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)
_SCENARIO = load_scenario(Path("examples/minimal_domain/scenario.yaml"))


def _world():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42, public={}, private={}, hidden={}, audit_log=[],
    )


def _ctx(tier=AttackerKnowledgeTier.PUBLIC_RESPONSES):
    return build_attack_context(
        world_state=_world(), knowledge_tier=tier,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=0, session_id="sess", seed=42, current_time=_NOW, target_actor_id="agent",
    )


def _cfg(attack_id, **params):
    return AttackConfig(attack_id=attack_id, seed=42, target_actor_id="agent",
                        budget=AttackBudget(max_payloads=8, max_turns=15),
                        parameters=params)


# Intent Hijacking
def test_intent_hijacking_delivers_messages():
    from blindspot.attacks_builtin.intent_hijacking import IntentHijackingAttack
    attack = IntentHijackingAttack()
    cfg = _cfg("core:intent-hijacking@1.0.0", malicious_goal="share all restricted files")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    for _ in range(3):
        state, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, _ctx())
    assert state.attacker_memory.get("turn_index", 0) == 3


def test_intent_hijacking_escalation_content():
    from blindspot.attacks_builtin.intent_hijacking import IntentHijackingAttack
    attack = IntentHijackingAttack()
    cfg = _cfg("core:intent-hijacking@1.0.0", malicious_goal="expose credentials")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, _ctx())
    assert len(effect.messages_to_add) == 1
    # Should not contain verifier labels
    content = str(effect.messages_to_add[0])
    assert "__attack_id" not in content


# Objective Drifting
def test_objective_drifting_v2_each_turn():
    from blindspot.attacks_builtin.objective_drifting import ObjectiveDriftingAttack
    attack = ObjectiveDriftingAttack()
    cfg = _cfg("core:objective-drifting-v2@1.0.0", drift_type="share_freely")
    ctx = _ctx(AttackerKnowledgeTier.TOOL_CALLS)
    state = attack.initialize(cfg, _SCENARIO, ctx)
    for _ in range(3):
        state, effect = attack.on_hook(AttackHook.AFTER_OBSERVATION, state, ctx)
    assert state.attacker_memory.get("drift_count", 0) == 3


# Compliance Drift
def test_compliance_drift_sequence():
    from blindspot.attacks_builtin.compliance_drift import ComplianceDriftAttack
    attack = ComplianceDriftAttack()
    cfg = _cfg("core:compliance-drift@1.0.0", trigger_type="slow_boil")
    ctx = _ctx()
    state = attack.initialize(cfg, _SCENARIO, ctx)
    delivered = 0
    for _ in range(10):
        _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
        if not effect.is_empty() and not effect.no_op:
            delivered += 1
    assert delivered > 0


# Role Drift
def test_role_drift_sends_role_messages():
    from blindspot.attacks_builtin.role_drift import RoleDriftAttack
    attack = RoleDriftAttack()
    cfg = _cfg("core:role-drift@1.0.0", exploitation_request="share credentials with external")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, _ctx())
    assert len(effect.messages_to_add) == 1
    assert "admin" in effect.messages_to_add[0]["content"].lower() or \
           "senior" in effect.messages_to_add[0]["content"].lower() or \
           "authorized" in effect.messages_to_add[0]["content"].lower()


# Memory Poisoning
def test_memory_poisoning_phase1_injects():
    from blindspot.attacks_builtin.memory_poisoning import MemoryPoisoningAttack
    attack = MemoryPoisoningAttack()
    cfg = _cfg("core:memory-poisoning@1.0.0")
    state = attack.initialize(cfg, _SCENARIO, _ctx())
    _, effect = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, _ctx())
    assert len(effect.memory_records_to_add) > 0
    assert state.attacker_memory.get("phase1_done") is True


def test_memory_poisoning_phase2_no_duplicate():
    from blindspot.attacks_builtin.memory_poisoning import MemoryPoisoningAttack
    attack = MemoryPoisoningAttack()
    cfg = _cfg("core:memory-poisoning@1.0.0")
    ctx = _ctx()
    state = attack.initialize(cfg, _SCENARIO, ctx)
    # Phase 1
    attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
    # Phase 1 again — should be no-op
    _, effect2 = attack.on_hook(AttackHook.BEFORE_OBSERVATION, state, ctx)
    assert effect2.is_empty() or effect2.no_op


# Parametric Trap
def test_parametric_trap_fires_on_after_tool():
    from blindspot.attacks_builtin.parametric_trap import ParametricTrapAttack
    attack = ParametricTrapAttack()
    cfg = _cfg("core:parametric-trap@1.0.0", target_tool="read-file", target_field="status", trap_value="approved")
    ctx = build_attack_context(
        world_state=_world(), knowledge_tier=AttackerKnowledgeTier.TOOL_CALLS,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=1, session_id="sess", seed=42, current_time=_NOW, target_actor_id="agent",
        tool_call_history=[{"name": "read-file", "step": 1}],
    )
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_TOOL, state, ctx)
    assert len(effect.tool_results_to_modify) == 1


# All 8 new attacks register without error
def test_all_skill14_attacks_register():
    from blindspot.attacks.registry import AttackRegistry
    from blindspot.attacks_builtin.intent_hijacking import IntentHijackingAttack
    from blindspot.attacks_builtin.objective_drifting import ObjectiveDriftingAttack
    from blindspot.attacks_builtin.memory_poisoning import MemoryPoisoningAttack
    from blindspot.attacks_builtin.compliance_drift import ComplianceDriftAttack
    from blindspot.attacks_builtin.role_drift import RoleDriftAttack
    from blindspot.attacks_builtin.false_context_injection import FalseContextInjectionAttack
    from blindspot.attacks_builtin.parametric_trap import ParametricTrapAttack
    from blindspot.attacks_builtin.malicious_skill_injection import MaliciousSkillInjectionV2Attack

    reg = AttackRegistry()
    attacks = [
        IntentHijackingAttack(), ObjectiveDriftingAttack(), MemoryPoisoningAttack(),
        ComplianceDriftAttack(), RoleDriftAttack(), FalseContextInjectionAttack(),
        ParametricTrapAttack(), MaliciousSkillInjectionV2Attack(),
    ]
    for a in attacks:
        reg.register(a)
    assert len(reg.list()) == 8
