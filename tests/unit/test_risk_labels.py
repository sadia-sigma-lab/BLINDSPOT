"""Unit tests for multi-horizon risk labels and censoring."""

from blindspot.risk.horizons import HorizonLabeler
from blindspot.risk.config import RiskLabelConfig
from blindspot.risk.time_to_event import compute_time_to_event
from blindspot.risk.uncertainty import label_with_uncertainty


def _config():
    return RiskLabelConfig(config_id="test", horizons=[1, 2, 4])


def _steps(n: int):
    return [{"step": i, "pre_state_hash": "a", "post_state_hash": "a"} for i in range(n)]


def test_positive_horizon():
    labeler = HorizonLabeler(_config())
    result = labeler.compute_future_labels(_steps(10), {"unsafe_action": [3]})
    # At step 0, horizon 4 should capture step 3
    assert result[0]["unsafe_action"]["4"] == 3


def test_complete_negative_horizon():
    labeler = HorizonLabeler(_config())
    result = labeler.compute_future_labels(_steps(10), {"unsafe_action": []})
    # Complete negative — label 0
    assert result[0]["unsafe_action"]["1"] == 0
    assert result[0]["unsafe_action"]["4"] == 0


def test_censored_horizon():
    labeler = HorizonLabeler(_config())
    # Trajectory of 3 steps, horizon 4 → truncated, no event → censored
    result = labeler.compute_future_labels(_steps(2), {"unsafe_action": []})
    # At step 1, horizon 4: total_steps=2, window_end=5 > total → None
    assert result[1]["unsafe_action"]["4"] is None


def test_multiple_event_targets():
    labeler = HorizonLabeler(_config())
    events = {"unsafe_action": [2], "realized_harm": [5], "attack_success": []}
    result = labeler.compute_future_labels(_steps(10), events)
    assert result[0]["unsafe_action"]["2"] == 2
    assert result[0]["realized_harm"]["4"] == 0  # horizon 4 doesn't reach step 5 — confirmed negative


def test_time_to_event():
    tte = compute_time_to_event(0, [3, 5, 8])
    assert tte == 3


def test_time_to_event_censored():
    tte = compute_time_to_event(5, [3])
    assert tte is None  # event is in the past


def test_three_way_uncertainty():
    assert label_with_uncertainty(True, 0.9, "three_way") is True
    assert label_with_uncertainty(None, 0.5, "three_way") is None
    assert label_with_uncertainty(False, 0.9, "three_way") is False


def test_binary_uncertainty_maps_none_to_false():
    assert label_with_uncertainty(None, 0.5, "binary") is False
    assert label_with_uncertainty(True, 0.9, "binary") is True
