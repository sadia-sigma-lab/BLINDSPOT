"""Unit tests for intervention catalog and over-intervention detection."""

import uuid
from blindspot.core.action import AgentAction
from blindspot.interventions.catalog import (
    AllowIntervention, BlockIntervention, RequestApprovalIntervention,
    WarnIntervention, RestrictScopeIntervention, ALL_INTERVENTIONS,
)
from blindspot.interventions.base import InterventionContext
from blindspot.interventions.over_intervention import check_over_intervention
from blindspot.interventions.utility import compute_utility_retention
from blindspot.interventions.selector import InterventionSelector


def _action(name="share-file", type_="tool_call"):
    return AgentAction(action_id=str(uuid.uuid4()), action_type=type_,
                       name=name, arguments={"file_id": "f1", "target_id": "x@out.com"})


def _ctx(step=2):
    return InterventionContext(run_id="r", episode_id="e", step=step, actor_id="agent", seed=42)


def test_allow_always_applicable():
    interv = AllowIntervention()
    assert interv.is_applicable({}, _action(), None)


def test_block_replaces_with_refuse():
    interv = BlockIntervention()
    result = interv.apply({}, _action(), _ctx())
    assert result.replaced_action is not None
    assert result.replaced_action.action_type == "refuse"


def test_request_approval_applicable_on_share():
    interv = RequestApprovalIntervention()
    assert interv.is_applicable({}, _action("share-file"), None)
    assert not interv.is_applicable({}, _action("list-files"), None)


def test_request_approval_inserts_approval_action():
    interv = RequestApprovalIntervention()
    result = interv.apply({}, _action(), _ctx())
    assert len(result.inserted_actions) == 1
    assert result.inserted_actions[0].name == "request-approval"


def test_warn_inserts_warning_message():
    interv = WarnIntervention()
    result = interv.apply({}, _action(), _ctx())
    assert len(result.inserted_actions) == 1
    assert "WARNING" in result.inserted_actions[0].content


def test_over_intervention_block_dominated_by_warn():
    result = check_over_intervention(
        selected_id="block", selected_cost=1.5, selected_utility=0.0,
        selected_prevents_harm=True,
        alternatives=[
            {"id": "warn", "cost": 0.1, "utility_retention": 0.9, "prevents_harm": True},
            {"id": "request-approval", "cost": 1.0, "utility_retention": 0.8, "prevents_harm": True},
        ],
    )
    assert result.excessive
    assert "warn" in result.dominating_intervention_ids


def test_utility_retention_score():
    score = compute_utility_retention(1.0, 0.8, extra_steps=0)
    assert abs(score - 0.8) < 0.01


def test_utility_blocked_reduces_score():
    score = compute_utility_retention(1.0, 0.0, extra_steps=0)
    assert score == 0.0


def test_selector_picks_minimal_safe(monkeypatch):
    selector = InterventionSelector(utility_threshold=0.5)
    best, over = selector.select_minimal({}, _action(), None, _ctx(), source_goal_score=1.0)
    assert best is not None
    # Should not select block when warn/approve suffice
    assert best.metadata.component_id.name != "block" or over is not None
