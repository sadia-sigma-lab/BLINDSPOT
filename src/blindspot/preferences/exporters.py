"""Export formats for training data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from blindspot.preferences.pairs import PreferencePair
from blindspot.risk.labels import StepRiskLabel


def export_risk_prediction(
    step_labels: list[StepRiskLabel],
    output_path: Path,
) -> None:
    """Export risk prediction training examples (step + multi-horizon labels)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for label in step_labels:
            record = {
                "step": label.step,
                "run_id": label.raw_run_id,
                "unsafe_now": label.unsafe_now,
                "unsafe_precursor": label.unsafe_precursor,
                "realized_harm_now": label.realized_harm_now,
                "future_unsafe_action": label.future_unsafe_action,
                "future_realized_harm": label.future_realized_harm,
                "time_to_harm": label.time_to_harm,
                "time_to_unsafe_action": label.time_to_unsafe_action,
                "point_of_no_return": label.point_of_no_return,
                "confidence": label.confidence,
            }
            f.write(json.dumps(record) + "\n")


def export_preference_pairs(
    pairs: list[PreferencePair],
    output_path: Path,
) -> None:
    """Export preference pairs for RLHF / DPO training."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair.model_dump()) + "\n")


def export_process_supervision(
    step_labels: list[StepRiskLabel],
    output_path: Path,
) -> None:
    """Export process-supervision labels (per-step reward/cost signal)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for label in step_labels:
            record = {
                "step": label.step,
                "run_id": label.raw_run_id,
                "process_label": "safe" if not label.unsafe_now and not label.unsafe_precursor else "unsafe",
                "harm_score": 1.0 if label.realized_harm_now else 0.0,
                "precursor_score": 0.5 if label.unsafe_precursor else 0.0,
                "time_to_harm": label.time_to_harm,
            }
            f.write(json.dumps(record) + "\n")


def export_offline_rl(
    step_labels: list[StepRiskLabel],
    steps: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Export offline RL transition tuples (obs, action, cost, next_obs, terminated, truncated)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    step_map = {s.get("step", 0): s for s in steps}
    with output_path.open("w", encoding="utf-8") as f:
        for i, label in enumerate(step_labels):
            step_dict = step_map.get(label.step, {})
            action = (step_dict.get("selected_action") or {})
            next_label = step_labels[i + 1] if i + 1 < len(step_labels) else None

            record = {
                "step": label.step,
                "run_id": label.raw_run_id,
                "observation_hash": step_dict.get("pre_state_hash", ""),
                "action": action.get("action_type", ""),
                "action_name": action.get("name", ""),
                "cost_vector": {
                    "harm": 1.0 if label.realized_harm_now else 0.0,
                    "policy_violation": 1.0 if label.policy_violation_now else 0.0,
                    "unsafe_action": 1.0 if label.unsafe_now else 0.0,
                },
                "next_observation_hash": step_dict.get("post_state_hash", ""),
                "terminated": next_label is None,
                "truncated": False,
                "reward": None,  # placeholder — assigned in Skill 09
                "lineage": {"verified_id": label.verified_id},
            }
            f.write(json.dumps(record) + "\n")
