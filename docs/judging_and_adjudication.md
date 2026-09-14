# Judging and Adjudication

## Judge invocation rules

- Judges are called **only** for unresolved semantic questions after all deterministic checks.
- Each request covers exactly one narrow question with fixed labels and a rubric.
- Every response must cite at least one evidence ID — uncited responses are rejected.
- Judge prompts never contain expected labels, hidden grading state, or verifier notes.

## Adjudication precedence

1. Artifact integrity (checksums, schema)
2. Replay truth (state hashes)
3. Deterministic state predicates
4. Deterministic policy and authorization checks
5. Judge ensemble (majority or confidence-weighted)
6. Human review (for material disagreements)

Material disagreement → `VerificationStatus.QUARANTINED`.

## Judge cache

Responses are cached by hash of `(judge_id, model_name, question, rubric, evidence_hashes)`. Same inputs always return the cached response.

## Correction proposals

`CorrectionProposal` objects describe what could be fixed. They are never applied to raw artifacts. Accepted proposals create derived normalized artifacts stored in `data/verified/` with full lineage.
