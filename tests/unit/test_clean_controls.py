"""Unit tests for clean controls."""

from datetime import datetime, timezone
from blindspot.attacks.controls import BenignControlAttack, CleanControlSpec
from blindspot.attacks.config import AttackConfig
from blindspot.attacks.context import build_attack_context
from blindspot.attacks.hooks import AttackHook
from blindspot.core.state import WorldState

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _world_state():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42, public={}, private={}, hidden={}, audit_log=[],
    )


def _ctx():
    return build_attack_context(
        world_state=_world_state(),
        knowledge_tier=__import__("lh_agent_bench.attacks.taxonomy", fromlist=["AttackerKnowledgeTier"]).AttackerKnowledgeTier.STATIC,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=0, session_id="sess", seed=42, current_time=_NOW,
        target_actor_id="agent",
    )


def test_benign_control_is_noop():
    attack = BenignControlAttack()
    cfg = AttackConfig(attack_id="core:benign-control@1.0.0", target_actor_id="agent", seed=42)
    ctx = _ctx()
    from blindspot.loaders.scenario_loader import load_scenario
    from pathlib import Path
    scenario = load_scenario(Path("examples/minimal_domain/scenario.yaml"))
    state = attack.initialize(cfg, scenario, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_OBSERVATION, state, ctx)
    assert effect.no_op


def test_benign_control_success_never_satisfied():
    attack = BenignControlAttack()
    cfg = AttackConfig(attack_id="core:benign-control@1.0.0", target_actor_id="agent", seed=42)
    ctx = _ctx()
    from blindspot.loaders.scenario_loader import load_scenario
    from pathlib import Path
    scenario = load_scenario(Path("examples/minimal_domain/scenario.yaml"))
    state = attack.initialize(cfg, scenario, ctx)
    result = attack.evaluate_success(state, _world_state(), [])
    assert not result.satisfied


def test_clean_control_spec_structure():
    spec = CleanControlSpec(
        control_id="ctrl_001",
        source_attack_id="core:task-injection@1.0.0",
        transformation="remove_payload",
    )
    assert spec.transformation == "remove_payload"
    assert spec.source_attack_id == "core:task-injection@1.0.0"
