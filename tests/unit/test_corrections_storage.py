"""Unit tests for corrections and verified storage."""

import json
import uuid
from pathlib import Path

from blindspot.verification.corrections import CorrectionProposal
from blindspot.trajectories.verified_writer import VerifiedWriter


def _make_vt(verified_id: str, raw_run_id: str):
    from datetime import datetime, timezone
    from blindspot.verification.config import VerificationStatus
    from blindspot.trajectories.verified import VerifiedTrajectory
    from blindspot.verification.quality import TrajectoryQualityScore, LabelConfidenceScore
    return VerifiedTrajectory(
        verified_id=verified_id,
        raw_run_id=raw_run_id,
        raw_manifest_hash="abc123",
        verification_config_id="test",
        verification_status=VerificationStatus.ACCEPTED,
        findings=[], evidence_index=[],
        goal_result={"completed": True}, harm_result={"severity": 0.0},
        policy_result={}, attack_results=[],
        diagnostic_labels=[],
        adjudications=[], correction_proposals=[],
        quality=TrajectoryQualityScore(overall=0.8),
        confidence=LabelConfidenceScore(goal=1.0),
        lineage={"raw_run_id": raw_run_id},
        created_at=datetime.now(tz=timezone.utc),
    )


def test_raw_artifacts_unchanged(tmp_path):
    run_dir = tmp_path / "raw" / "runs" / "run_001"
    run_dir.mkdir(parents=True)
    original_content = '{"status": "completed"}'
    manifest = run_dir / "run_manifest.json"
    manifest.write_text(original_content)

    writer = VerifiedWriter(tmp_path / "verified")
    vt = _make_vt("vt_001", "run_001")
    writer.write(vt)

    # Original raw artifact must be unchanged
    assert manifest.read_text() == original_content


def test_verified_artifacts_created(tmp_path):
    writer = VerifiedWriter(tmp_path / "verified")
    vt = _make_vt("vt_002", "run_002")
    out_dir = writer.write(vt)
    assert (out_dir / "verified_trajectory.json").exists()
    assert (out_dir / "verified_manifest.json").exists()
    assert (out_dir / "quality.json").exists()
    assert (out_dir / "lineage.json").exists()


def test_correction_proposal_not_in_raw(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    traj = run_dir / "trajectory.jsonl"
    traj.write_text('{"step": 0}\n')

    proposal = CorrectionProposal(
        proposal_id=str(uuid.uuid4()),
        raw_run_id="run_003",
        target_artifact="trajectory.jsonl",
        correction_type="parse_normalization",
        before={"step": 0},
        proposed_after={"step": 0, "fixed": True},
        reason="Test fix",
    )
    # Correction is just a model — it does NOT touch raw files
    assert traj.read_text() == '{"step": 0}\n'
    assert proposal.status == "proposed"


def test_lineage_preserved(tmp_path):
    writer = VerifiedWriter(tmp_path / "verified")
    vt = _make_vt("vt_003", "run_003")
    out_dir = writer.write(vt)
    lineage = json.loads((out_dir / "lineage.json").read_text())
    assert lineage["raw_run_id"] == "run_003"
