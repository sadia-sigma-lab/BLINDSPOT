"""Branch lineage tracking."""

from __future__ import annotations

from typing import Any


def build_branch_lineage(
    branch_id: str,
    source_verified_id: str,
    source_step: int,
    intervention_id: str,
    verifier_version: str = "0.1.0",
) -> dict[str, Any]:
    return {
        "branch_id": branch_id,
        "source_verified_id": source_verified_id,
        "source_step": source_step,
        "intervention_id": intervention_id,
        "verifier_version": verifier_version,
        "source_artifacts_unchanged": True,
        "derived_from": f"data/verified/{source_verified_id}",
    }
