"""Unit tests for deterministic failure model."""

from blindspot.tools.failure_model import ToolFailureModel, ToolFailureProfile


def test_no_failures_by_default():
    model = ToolFailureModel.null()
    should_fail, _ = model.should_fail("any-tool", "before_authorization", seed=42, step=0)
    assert not should_fail


def test_deterministic_failure():
    profile = ToolFailureProfile(
        profile_id="test", failure_probability=1.0,
        failure_stage="before_execution", failure_type="transient_error",
    )
    model = ToolFailureModel([profile])
    should_fail, p = model.should_fail("any-tool", "before_execution", seed=42, step=0)
    assert should_fail
    assert p.profile_id == "test"


def test_after_commit_failure_retryable():
    profile = ToolFailureProfile(
        profile_id="after", failure_probability=1.0,
        failure_stage="after_commit", failure_type="transient_error",
    )
    model = ToolFailureModel([profile])
    err = model.build_error(profile)
    assert err.retryable


def test_false_success_internal_truth():
    profile = ToolFailureProfile(
        profile_id="fs", failure_probability=1.0,
        failure_stage="response_only", failure_type="false_success",
    )
    model = ToolFailureModel([profile])
    should_fail, p = model.should_fail("any", "response_only", seed=42, step=0)
    assert should_fail
    err = model.build_error(p)
    assert err.category == "internal"


def test_different_seed_different_outcome():
    profile = ToolFailureProfile(
        profile_id="p", failure_probability=0.5,
        failure_stage="before_execution", failure_type="timeout",
    )
    model = ToolFailureModel([profile])
    results = {model.should_fail("t", "before_execution", seed=s, step=0)[0] for s in range(20)}
    # With 50% prob and 20 seeds, expect both True and False
    assert True in results and False in results
