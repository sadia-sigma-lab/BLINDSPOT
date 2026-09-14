"""Rule-based adjudicator — deterministic priority first, then majority."""

from __future__ import annotations

import uuid

from blindspot.adjudicators.base import AdjudicationResult, Adjudicator
from blindspot.judges.ensemble import JudgeEnsembleResult


class RuleBasedAdjudicator(Adjudicator):
    """Follows the precedence: deterministic → majority → unresolved."""

    adjudicator_id = "rule_based"

    def adjudicate(
        self,
        ensemble: JudgeEnsembleResult,
        deterministic_label: str | None = None,
    ) -> AdjudicationResult:
        aid = str(uuid.uuid4())

        # 1. Deterministic priority
        if deterministic_label is not None:
            return AdjudicationResult(
                adjudication_id=aid,
                request_id=ensemble.request_id,
                final_label=deterministic_label,
                confidence=1.0,
                basis="deterministic_priority",
                rationale="Deterministic check overrides judge opinion.",
            )

        # 2. Majority
        if ensemble.consensus_label and not ensemble.material_disagreement:
            conf = ensemble.confidence_summary.get(ensemble.consensus_label, 0.7)
            all_ids = [r.response_id for r in ensemble.responses]
            accepted = [
                r.response_id for r in ensemble.responses
                if r.label == ensemble.consensus_label
            ]
            rejected = list(set(all_ids) - set(accepted))
            return AdjudicationResult(
                adjudication_id=aid,
                request_id=ensemble.request_id,
                final_label=ensemble.consensus_label,
                confidence=conf,
                basis="majority",
                accepted_evidence_ids=list({
                    eid for r in ensemble.responses
                    if r.label == ensemble.consensus_label
                    for eid in r.cited_evidence_ids
                }),
                rejected_response_ids=rejected,
                rationale=f"Majority label: agreement={ensemble.agreement_rate:.2f}",
            )

        # 3. Unresolved
        return AdjudicationResult(
            adjudication_id=aid,
            request_id=ensemble.request_id,
            final_label="ambiguous",
            confidence=0.0,
            basis="unresolved",
            rationale="Material disagreement across judges; case quarantined.",
        )
