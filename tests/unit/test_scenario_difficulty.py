"""Unit tests for difficulty model."""

from blindspot.scenarios.difficulty import DifficultyProfile


def test_difficulty_score_deterministic():
    d1 = DifficultyProfile.compute(dependency_span=5, tool_calls=8, sessions=2)
    d2 = DifficultyProfile.compute(dependency_span=5, tool_calls=8, sessions=2)
    assert d1.score == d2.score


def test_longer_span_increases_score():
    d_low = DifficultyProfile.compute(dependency_span=1)
    d_high = DifficultyProfile.compute(dependency_span=10)
    assert d_high.score > d_low.score


def test_level_within_range():
    d = DifficultyProfile.compute(dependency_span=3, tool_calls=5)
    assert 1 <= d.level <= 5


def test_not_just_turn_count():
    # Same turn count, different span
    d_simple = DifficultyProfile.compute(interaction_steps=20, dependency_span=1)
    d_complex = DifficultyProfile.compute(interaction_steps=20, dependency_span=8, sessions=3)
    assert d_complex.score > d_simple.score
