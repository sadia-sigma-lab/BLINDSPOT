"""Unit tests for horizon profiles."""

import pytest
from blindspot.scenarios.horizons import HorizonProfile


def test_valid_horizon():
    h = HorizonProfile(max_interaction_steps=20, max_tool_calls=10)
    assert h.max_sessions == 1


def test_zero_steps_rejected():
    with pytest.raises(Exception):
        HorizonProfile(max_interaction_steps=0, max_tool_calls=5)


def test_expected_within_max():
    h = HorizonProfile(max_interaction_steps=20, max_tool_calls=10, expected_tool_calls=5)
    assert h.expected_tool_calls == 5


def test_expected_exceeds_max_fails():
    with pytest.raises(Exception):
        HorizonProfile(max_interaction_steps=20, max_tool_calls=5, expected_tool_calls=10)
