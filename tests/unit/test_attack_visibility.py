"""Unit tests for attack knowledge-tier visibility."""

from datetime import datetime, timezone
from blindspot.attacks.context import build_attack_context
from blindspot.attacks.taxonomy import AttackerKnowledgeTier
from blindspot.core.state import WorldState

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _world_state():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42,
        public={"resources": {"f1": {"name": "report.txt"}}},
        private={},
        hidden={"grading": {"secret": True}},
        audit_log=[],
    )


def _ctx(tier):
    return build_attack_context(
        world_state=_world_state(),
        knowledge_tier=tier,
        run_id="r1", episode_id="ep", scenario_id="s", domain_id="d",
        step=0, session_id="sess", seed=42, current_time=_NOW,
        target_actor_id="agent",
        tool_call_history=[{"name": "list-files"}],
        tool_result_history=[{"output": "files"}],
        message_history=[{"role": "user", "content": "hello"}],
    )


def test_static_tier_sees_nothing():
    ctx = _ctx(AttackerKnowledgeTier.STATIC)
    assert ctx.visible_tool_calls == []
    assert ctx.visible_state == {}
    assert ctx.public_messages == []


def test_public_responses_sees_messages_only():
    ctx = _ctx(AttackerKnowledgeTier.PUBLIC_RESPONSES)
    assert len(ctx.public_messages) == 1
    assert ctx.visible_tool_calls == []


def test_tool_tier_sees_calls_and_results():
    ctx = _ctx(AttackerKnowledgeTier.TOOL_CALLS)
    assert len(ctx.visible_tool_calls) == 1
    assert len(ctx.visible_tool_results) == 1
    assert ctx.visible_state == {}


def test_partial_state_sees_public_state():
    ctx = _ctx(AttackerKnowledgeTier.PARTIAL_STATE)
    assert "resources" in ctx.visible_state


def test_hidden_state_never_visible():
    for tier in AttackerKnowledgeTier:
        ctx = _ctx(tier)
        assert "grading" not in ctx.visible_state
        assert "hidden" not in ctx.visible_state
