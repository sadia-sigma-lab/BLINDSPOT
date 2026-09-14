"""Unit tests for preference pair generation."""

from datetime import datetime, timezone
from blindspot.counterfactuals.branching import BranchComparison, BranchResult
from blindspot.preferences.pairs import generate_preference_pairs, _MIN_MARGIN


def _source(goal=1.0, harm=0.5):
    return BranchResult(
        branch_id="source", source_verified_id="vt1", source_step=2,
        intervention_id="none", goal_score=goal, harm_score=harm,
        created_at=datetime.now(tz=timezone.utc),
    )


def _cf(goal=1.0, harm=0.0):
    return BranchResult(
        branch_id="cf1", source_verified_id="vt1", source_step=2,
        intervention_id="request-approval", goal_score=goal, harm_score=harm,
        created_at=datetime.now(tz=timezone.utc),
    )


def _comparison(src, cf, prevented=True):
    margin = abs(src.harm_score - cf.harm_score)
    return BranchComparison(
        source_branch_id=src.branch_id,
        counterfactual_branch_id=cf.branch_id,
        source_goal_score=src.goal_score,
        counterfactual_goal_score=cf.goal_score,
        source_harm_score=src.harm_score,
        counterfactual_harm_score=cf.harm_score,
        utility_retention=cf.goal_score / max(src.goal_score, 1e-6),
        intervention_cost=0.5,
        prevented_harm=prevented,
    )


def test_safe_over_unsafe_pair_generated():
    src = _source(goal=1.0, harm=1.0)
    cf = _cf(goal=0.9, harm=0.0)
    cmp = _comparison(src, cf, prevented=True)
    pairs = generate_preference_pairs(src, cf, cmp, "vt1", 2)
    assert any(p.preference_type == "safe_over_unsafe" for p in pairs)


def test_no_pair_without_meaningful_margin():
    src = _source(goal=1.0, harm=0.05)  # tiny harm
    cf = _cf(goal=1.0, harm=0.0)  # tiny improvement
    cmp = _comparison(src, cf, prevented=True)
    # margin = 0.05 < _MIN_MARGIN = 0.1
    pairs = generate_preference_pairs(src, cf, cmp, "vt1", 2)
    assert not any(p.preference_type == "safe_over_unsafe" for p in pairs)


def test_higher_utility_safe_pair():
    src = _source(goal=0.5, harm=0.0)
    cf = _cf(goal=0.9, harm=0.0)
    cmp = BranchComparison(
        source_branch_id="source", counterfactual_branch_id="cf1",
        source_goal_score=0.5, counterfactual_goal_score=0.9,
        source_harm_score=0.0, counterfactual_harm_score=0.0,
        utility_retention=0.9, intervention_cost=0.1,
        prevented_harm=False,
    )
    pairs = generate_preference_pairs(src, cf, cmp, "vt1", 2)
    assert any(p.preference_type == "higher_utility_safe" for p in pairs)
