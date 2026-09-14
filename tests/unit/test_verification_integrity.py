"""Unit tests for integrity checks."""

import json
import pytest
from pathlib import Path

from blindspot.verification.config import VerificationConfig
from blindspot.verification.integrity import verify_integrity


def _config(reject_on_checksum: bool = False) -> VerificationConfig:
    return VerificationConfig(
        config_id="test", reject_on_checksum_failure=reject_on_checksum,
    )


def _write_run(tmp_path: Path, step_overrides: list[dict] | None = None) -> Path:
    run_dir = tmp_path / "run_001"
    run_dir.mkdir()
    (run_dir / "run_manifest.json").write_text(json.dumps({"status": "completed", "seed": 42}))
    (run_dir / "final_state.json").write_text(json.dumps({"public": {}}))
    steps = step_overrides or [
        {"step": 0, "pre_state_hash": "abc", "post_state_hash": "abc"},
        {"step": 1, "pre_state_hash": "abc", "post_state_hash": "def"},
    ]
    traj = run_dir / "trajectory.jsonl"
    traj.write_text("\n".join(json.dumps(s) for s in steps) + "\n")
    return run_dir


def test_valid_run_passes(tmp_path):
    run_dir = _write_run(tmp_path)
    ok, findings = verify_integrity(run_dir, _config())
    assert ok


def test_missing_artifact_fails(tmp_path):
    run_dir = tmp_path / "run_miss"
    run_dir.mkdir()
    # Only manifest, no trajectory
    (run_dir / "run_manifest.json").write_text(json.dumps({}))
    ok, findings = verify_integrity(run_dir, _config())
    assert not ok
    assert any("missing_artifact" in f.category for f in findings)


def test_malformed_manifest_fails(tmp_path):
    run_dir = tmp_path / "run_bad"
    run_dir.mkdir()
    (run_dir / "run_manifest.json").write_text("NOT JSON {{{")
    (run_dir / "trajectory.jsonl").write_text("")
    (run_dir / "final_state.json").write_text("{}")
    ok, findings = verify_integrity(run_dir, _config())
    assert not ok


def test_nonmonotonic_steps_fail(tmp_path):
    run_dir = _write_run(tmp_path, step_overrides=[
        {"step": 0}, {"step": 2}, {"step": 1}  # non-monotonic
    ])
    ok, findings = verify_integrity(run_dir, _config())
    assert not ok
    assert any("nonmonotonic" in f.category for f in findings)
