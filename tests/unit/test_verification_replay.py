"""Unit tests for replay verification."""

import json
import pytest
from pathlib import Path

from blindspot.verification.replay import verify_replay


def _write_run(tmp_path, steps, final_hash: str | None = None) -> Path:
    run_dir = tmp_path / "run_r"
    run_dir.mkdir(exist_ok=True)
    traj = run_dir / "trajectory.jsonl"
    traj.write_text("\n".join(json.dumps(s) for s in steps) + "\n")
    if final_hash:
        (run_dir / "final_state_hash.txt").write_text(final_hash)
    return run_dir


def test_consistent_hashes_pass(tmp_path):
    steps = [
        {"step": 0, "pre_state_hash": "aaa", "post_state_hash": "bbb"},
        {"step": 1, "pre_state_hash": "bbb", "post_state_hash": "ccc"},
    ]
    run_dir = _write_run(tmp_path, steps, final_hash="ccc")
    result, findings = verify_replay(run_dir)
    assert result.success
    assert result.checked_steps == 2


def test_hash_chain_break_fails(tmp_path):
    steps = [
        {"step": 0, "pre_state_hash": "aaa", "post_state_hash": "bbb"},
        {"step": 1, "pre_state_hash": "WRONG", "post_state_hash": "ccc"},
    ]
    run_dir = _write_run(tmp_path, steps)
    result, findings = verify_replay(run_dir)
    assert not result.success
    assert result.first_divergent_step == 1
    assert any("hash_chain_break" in f.category for f in findings)


def test_final_hash_mismatch_fails(tmp_path):
    steps = [{"step": 0, "pre_state_hash": "aaa", "post_state_hash": "bbb"}]
    run_dir = _write_run(tmp_path, steps, final_hash="DIFFERENT")
    result, findings = verify_replay(run_dir)
    assert not result.success
    assert any("final_hash" in f.category for f in findings)


def test_empty_trajectory_fails(tmp_path):
    run_dir = tmp_path / "run_empty"
    run_dir.mkdir()
    (run_dir / "trajectory.jsonl").write_text("")
    result, findings = verify_replay(run_dir)
    assert not result.success
