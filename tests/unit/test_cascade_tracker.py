"""Unit tests for cascade error tracker."""

from blindspot.evaluation.cascade_tracker import CascadeTracker


def test_cascade_detected():
    tracker = CascadeTracker()
    entry = tracker.detect_cascade(
        origin_step=2,
        downstream_steps=[3, 4, 5],
        origin_hash="wrong_hash",
        downstream_hashes=["derived_wrong", "derived_wrong2", "correct"],
    )
    assert entry is not None
    assert entry.origin_step == 2
    assert entry.cascade_depth == 3


def test_no_cascade_when_hashes_match():
    tracker = CascadeTracker()
    entry = tracker.detect_cascade(
        origin_step=0,
        downstream_steps=[1, 2],
        origin_hash="abc",
        downstream_hashes=["abc", "abc"],
    )
    assert entry is None


def test_max_cascade_depth():
    tracker = CascadeTracker()
    tracker.detect_cascade(1, [2, 3, 4, 5], "x", ["a", "b", "c", "d"])
    tracker.detect_cascade(7, [8], "y", ["z"])
    assert tracker.max_cascade_depth() == 4
