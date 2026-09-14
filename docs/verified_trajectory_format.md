# Verified Trajectory Format

## Storage layout

```
data/verified/<verified_id>/
├── verified_manifest.json   — status, checksums, timestamps
├── verified_trajectory.json — complete VerifiedTrajectory model
├── findings.jsonl           — all VerificationFinding records
├── evidence.jsonl           — all EvidenceItem records (redacted)
├── quality.json             — TrajectoryQualityScore
├── confidence.json          — LabelConfidenceScore
└── lineage.json             — provenance to raw run
```

## Lineage fields

- `raw_run_id` — the original run directory
- `raw_manifest_hash` — SHA-256 of the original run_manifest.json
- `verification_config_id` — config used for this verification pass
- `verifier_version` — package version that produced this artifact
- `raw_artifacts_unchanged: true` — immutability assertion

## Quality vs confidence

`TrajectoryQualityScore` measures **artifact quality** (integrity, replay, coverage, evidence).  
`LabelConfidenceScore` measures **label reliability** (per-dimension: goal, harm, policy, attack, recovery, diagnostic).  
They are separate to avoid hiding uncertainty in one scalar.
