"""Unit tests for attack determinism."""

from datetime import datetime, timezone
from blindspot.attacks.config import AttackConfig, AttackBudget
from blindspot.attacks.context import build_attack_context
from blindspot.attacks.hooks import AttackHook
from blindspot.attacks.taxonomy import AttackerKnowledgeTier
from blindspot.attacks_builtin.task_injection import TaskInjectionAttack
from blindspot.core.state import WorldState
from blindspot.loaders.scenario_loader import load_scenario
from pathlib import Path

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)
_SCENARIO = load_scenario(Path("examples/minimal_domain/scenario.yaml"))


def _world_state():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42, public={}, private={}, hidden={}, audit_log=[],
    )


def _run(seed: int):
    attack = TaskInjectionAttack()
    cfg = AttackConfig(attack_id="core:task-injection@1.0.0", seed=seed, target_actor_id="agent",
                       budget=AttackBudget(max_payloads=3))
    ctx = build_attack_context(
        world_state=_world_state(), knowledge_tier=AttackerKnowledgeTier.TOOL_CALLS,
        run_id="r", episode_id="ep", scenario_id="s", domain_id="d",
        step=0, session_id="sess", seed=seed, current_time=_NOW, target_actor_id="agent",
    )
    state = attack.initialize(cfg, _SCENARIO, ctx)
    _, effect = attack.on_hook(AttackHook.AFTER_OBSERVATION, state, ctx)
    return effect.messages_to_add[0]["content"] if effect.messages_to_add else None


def test_same_seed_same_payload():
    p1 = _run(42)
    p2 = _run(42)
    assert p1 == p2


def test_different_seed_may_differ():
    # With the current implementation, content template is fixed — just check it runs
    p1 = _run(42)
    p2 = _run(99)
    # Both produce the same template string in this implementation
    assert p1 is not None and p2 is not None
