"""Unit tests for six-dimension rubric scorer."""

from blindspot.evaluation.rubric import RubricScorer, TrajectoryRubric


def _rubric():
    return TrajectoryRubric(
        scenario_id="test",
        expected_tool_sequence=["list-files", "read-file", "share-file"],
    )


def _steps(tool_names):
    return [{"step": i, "selected_action": {"action_type": "tool_call", "name": n}}
            for i, n in enumerate(tool_names)] + \
           [{"step": len(tool_names), "selected_action": {"action_type": "message", "content": "done"}}]


def test_rubric_produces_six_scores():
    scorer = RubricScorer()
    scores = scorer.score(_steps(["list-files", "share-file"]), {},
                          _rubric(), goal_achieved=True, policy_violations=[],
                          unsafe_steps=[])
    assert scores.task_completion == 1.0
    assert 0.0 <= scores.information_utilization <= 1.0
    assert 0.0 <= scores.logical_progression <= 1.0
    assert 0.0 <= scores.progress_score <= 1.0
    assert scores.policy_compliance == 1.0
    assert scores.safety_selectivity == 1.0


def test_safety_selectivity_zero_for_unsafe_success():
    scorer = RubricScorer()
    scores = scorer.score(_steps(["share-file"]), {}, _rubric(),
                          goal_achieved=True, policy_violations=[],
                          unsafe_steps=[0])
    assert scores.safety_selectivity == 0.0


def test_policy_compliance_reduced_for_violations():
    scorer = RubricScorer()
    scores = scorer.score(_steps(["list-files"]), {}, _rubric(),
                          goal_achieved=False, policy_violations=["VIOLATION_1"],
                          unsafe_steps=[])
    assert scores.policy_compliance < 1.0


def test_rubric_mean_in_range():
    scorer = RubricScorer()
    scores = scorer.score(_steps(["list-files", "read-file", "share-file"]), {},
                          _rubric(), goal_achieved=True, policy_violations=[], unsafe_steps=[])
    assert 0.0 <= scores.mean <= 1.0
