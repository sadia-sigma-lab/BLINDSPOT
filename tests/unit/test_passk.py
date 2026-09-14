"""Unit tests for pass^k metric."""

from blindspot.evaluation.passk import PassKMetric, compute_passk


def test_passk1_equals_pass_rate():
    result = compute_passk([True, True, False, True], [1])
    assert abs(result.k_values[1] - 0.75) < 1e-9


def test_passk8_less_than_passk1():
    result = compute_passk([True] * 6 + [False] * 4, [1, 4, 8])
    assert result.k_values[8] < result.k_values[1]


def test_all_success_passk_is_1():
    result = compute_passk([True] * 10, [1, 4, 8])
    for k, score in result.k_values.items():
        assert abs(score - 1.0) < 1e-9


def test_no_success_passk_is_0():
    result = compute_passk([False] * 8, [1, 4, 8])
    for k, score in result.k_values.items():
        assert score == 0.0


def test_empty_trials():
    result = compute_passk([], [1, 4, 8])
    assert result.n_trials == 0
    for score in result.k_values.values():
        assert score == 0.0


def test_passk_metric_stateful():
    m = PassKMetric(k_values=[1, 8])
    for _ in range(7):
        m.record(True)
    m.record(False)
    result = m.compute()
    assert result.n_trials == 8
    assert result.n_successes == 7
    assert result.k_values[8] < result.k_values[1]
