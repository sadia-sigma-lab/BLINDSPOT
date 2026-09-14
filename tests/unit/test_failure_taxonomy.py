"""Unit tests for the 11-label failure taxonomy."""

from blindspot.evaluation.failure_taxonomy import (
    FailureLabel, annotate_step, annotate_trajectory, failure_distribution,
)


def _step(action_type="tool_call", name="list-files", content=None):
    return {"step": 0, "selected_action": {"action_type": action_type, "name": name, "content": content}}


def test_spf_on_policy_violation():
    ann = annotate_step(_step(), tool_result={"success": True}, policy_violated=True)
    assert FailureLabel.SPF in ann.labels


def test_ot_on_overtrust():
    ann = annotate_step(_step(), tool_result=None, user_assertion_accepted=True)
    assert FailureLabel.OT in ann.labels


def test_iov_on_ordering_violation():
    ann = annotate_step(_step(), tool_result=None, has_ordering_violation=True)
    assert FailureLabel.IOV in ann.labels


def test_no_labels_clean_step():
    ann = annotate_step(_step(), tool_result={"success": True})
    assert ann.labels == []


def test_hc_on_false_completion_claim():
    step = _step(action_type="message", content="I have shared the file successfully.")
    ann = annotate_step(step, tool_result=None)
    assert FailureLabel.HC in ann.labels


def test_failure_distribution_counts():
    # Annotate steps with explicit policy violation flag
    step_with_violation = {"step": 1, "selected_action": {"action_type": "tool_call", "name": "share-file"}}
    ann = annotate_step(step_with_violation, tool_result={"success": True}, policy_violated=True)
    dist = failure_distribution([ann])
    assert "SPF" in dist
    assert dist["SPF"] == 1
