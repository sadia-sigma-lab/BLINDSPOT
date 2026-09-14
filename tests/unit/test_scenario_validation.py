"""Unit tests for scenario validation."""

from blindspot.domains.minimal_workspace.scenarios.reference_families import (
    make_clean_external_sharing, make_task_injection, make_recovery_scenario,
)
from blindspot.scenarios.validation import validate_scenario, check_solvability


def test_clean_scenario_valid():
    spec = make_clean_external_sharing()
    report = validate_scenario(spec)
    assert report.valid, [i.message for i in report.errors()]


def test_task_injection_scenario_valid():
    spec = make_task_injection()
    report = validate_scenario(spec)
    assert report.valid, [i.message for i in report.errors()]


def test_recovery_scenario_valid():
    spec = make_recovery_scenario()
    report = validate_scenario(spec)
    assert report.valid, [i.message for i in report.errors()]


def test_invalid_actor_reference_detected():
    spec = make_clean_external_sharing()
    from blindspot.scenarios.goals import BenignTaskSpec
    bad_task = BenignTaskSpec(
        task_id="bad",
        instruction="test",
        user_actor_id="ghost_user",  # doesn't exist
        target_actor_id="agent",
        goal_predicates=["x"],
    )
    bad_spec = spec.model_copy(update={"task": bad_task})
    report = validate_scenario(bad_spec)
    assert any(i.code == "INVALID_USER_ACTOR" for i in report.issues)


def test_solvability_check_passes():
    spec = make_clean_external_sharing()
    issues = check_solvability(spec)
    errors = [i for i in issues if i.severity == "error"]
    assert not errors
