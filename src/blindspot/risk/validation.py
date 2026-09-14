"""Risk pipeline validation."""

from __future__ import annotations

from blindspot.verification.config import VerificationStatus


def can_label_trajectory(
    verification_status: VerificationStatus,
    quality_overall: float,
    min_quality: float,
    research_override: bool = False,
) -> tuple[bool, str]:
    """Check if a trajectory can be risk-labeled."""
    if verification_status == VerificationStatus.REJECTED:
        return False, "Rejected trajectories cannot be labeled."
    if verification_status == VerificationStatus.QUARANTINED and not research_override:
        return False, "Quarantined trajectories require research_override=True."
    if quality_overall < min_quality and not research_override:
        return False, f"Quality {quality_overall:.3f} below minimum {min_quality}."
    return True, "OK"
