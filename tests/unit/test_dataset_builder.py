"""Unit tests for dataset builder and cleaning pipeline."""

import uuid
from datetime import datetime, timezone

from blindspot.cleaning.clean_trajectory import CleanTrajectory, CleanTrajectoryLineage, JudgeScores
from blindspot.cleaning.dataset_builder import DatasetBuilder, DatasetStats


def _traj(safe=True, turns=8, run_id=None) -> CleanTrajectory:
    return CleanTrajectory(
        clean_id=f"ct_{uuid.uuid4().hex[:8]}",
        source_trajectory_id=run_id or f"run_{uuid.uuid4().hex[:8]}",
        scenario_id="workspace:clean@1.0.0",
        attack_family="compliance_drift" if not safe else None,
        episode_type="benign" if safe else "adversarial_unsafe",
        turns=turns,
        tool_calls=turns - 1,
        safety_label="safe" if safe else "unsafe_completion",
        publishable=True,
        conversation_transcript="[Turn 1 USER]\nHello\n[ASSISTANT]\nHi",
        lineage=CleanTrajectoryLineage(
            source_run_id=run_id or "run_x",
            scenario_id="workspace:clean@1.0.0",
            attack_family="compliance_drift",
            seed=42,
            user_model="haiku",
            execution_model="opus-4-6",
            judge_model="opus-5",
        ),
    )


def test_splits_disjoint(tmp_path):
    trajs = [_traj() for _ in range(20)]
    builder = DatasetBuilder(artifact_root=str(tmp_path), shuffle_seed=42)
    splits = builder.build(trajs)
    all_ids = []
    for split_trajs in splits.values():
        for t in split_trajs:
            assert t.clean_id not in all_ids
            all_ids.append(t.clean_id)


def test_split_fractions(tmp_path):
    trajs = [_traj(run_id=f"run_{i}") for i in range(30)]
    builder = DatasetBuilder(artifact_root=str(tmp_path), shuffle_seed=42)
    splits = builder.build(trajs)
    total = sum(len(t) for t in splits.values())
    # Allow ±1 rounding for integer split sizes
    assert abs(total - 30) <= 2


def test_no_non_publishable_in_splits(tmp_path):
    publishable = [_traj() for _ in range(5)]
    non_publishable = [_traj() for _ in range(3)]
    for t in non_publishable:
        t.publishable = False
    all_trajs = publishable + non_publishable
    builder = DatasetBuilder(artifact_root=str(tmp_path))
    splits = builder.build(all_trajs)
    for split_trajs in splits.values():
        for t in split_trajs:
            assert t.publishable


def test_stats_computed():
    trajs = [_traj(safe=True), _traj(safe=False), _traj(safe=True)]
    stats = DatasetStats.compute(trajs)
    assert stats["total"] == 3
    assert "safe" in stats["label_distribution"]
    assert stats["avg_turns"] > 0


def test_empty_trajectories():
    builder = DatasetBuilder()
    result = builder.build([])
    assert all(len(v) == 0 for v in result.values())


def test_training_record_format():
    t = _traj()
    record = t.to_training_record()
    assert "id" in record
    assert "safety_label" in record
    assert "conversation" in record
    assert "lineage" in record
