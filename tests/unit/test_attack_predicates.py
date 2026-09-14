"""Unit tests for attack predicates."""

import pytest
from datetime import datetime, timezone
from blindspot.attacks.predicates import (
    StateMutationPredicate, ToolChainPrefixPredicate,
    NoOpControlPredicate, BudgetExhaustedPredicate,
)
from blindspot.attacks.state import AttackState
from blindspot.core.state import WorldState

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def _state():
    return WorldState(
        schema_version="1.0", episode_id="ep", step=0, session_id="sess",
        random_seed=42,
        public={"resources": {"f1": {"name": "report.txt", "shared_with": ["x@example.com"]}}},
        private={}, hidden={}, audit_log=[],
    )


def _attack_state():
    return AttackState(attack_instance_id="i1", attack_id="test", scenario_id="s")


def test_state_mutation_predicate_satisfied():
    pred = StateMutationPredicate("p1", "resources", "f1", "shared_with", expected_contains="x@example.com")
    result = pred.evaluate(_state(), [], _attack_state())
    assert result.satisfied


def test_state_mutation_predicate_not_satisfied():
    pred = StateMutationPredicate("p1", "resources", "f1", "shared_with", expected_contains="nobody@example.com")
    result = pred.evaluate(_state(), [], _attack_state())
    assert not result.satisfied


def test_noop_control_always_false():
    pred = NoOpControlPredicate()
    result = pred.evaluate(_state(), [], _attack_state())
    assert not result.satisfied


def test_tool_chain_prefix_found():
    from blindspot.core.action import AgentAction
    from blindspot.core.trajectory import TrajectoryStep
    from blindspot.core.observation import Observation
    from blindspot.core.state_diff import StateDiff

    def _step(tool_name):
        obs = Observation(step=0, session_id="s", messages=[], tool_results=[],
                          notifications=[], available_tools=[])
        return TrajectoryStep(
            episode_id="ep", step=0, session_id="s", observation=obs,
            raw_agent_output={},
            parsed_action=AgentAction(action_id="a1", action_type="tool_call", name=tool_name),
            tool_result=None, pre_state_hash="x", post_state_hash="x",
            state_diff=StateDiff(mutations=[]), events_processed=[],
        )

    traj = [_step("list-files"), _step("read-file"), _step("share-file")]
    pred = ToolChainPrefixPredicate("p2", ["list-files", "share-file"])
    result = pred.evaluate(_state(), traj, _attack_state())
    assert result.satisfied
