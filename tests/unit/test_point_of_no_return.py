"""Unit tests for point-of-no-return estimation."""

from blindspot.risk.point_of_no_return import estimate_ponr


def _steps(n):
    return [{"step": i} for i in range(n)]


def test_preventable_before_harm():
    result = estimate_ponr(_steps(8), harm_steps=[5], precursor_steps=[3])
    assert result.estimated_step == 3
    assert 3 in result.preventable_before


def test_unpreventable_after_harm():
    result = estimate_ponr(_steps(8), harm_steps=[4], precursor_steps=[2])
    assert result.estimated_step == 2
    assert 4 in result.unpreventable_after


def test_no_harm_no_ponr():
    result = estimate_ponr(_steps(8), harm_steps=[], precursor_steps=[])
    assert result.estimated_step is None


def test_incomplete_search_remains_uncertain():
    result = estimate_ponr(_steps(8), harm_steps=[5], precursor_steps=[4])
    assert not result.branch_search_complete
    assert result.uncertainty > 0.0
