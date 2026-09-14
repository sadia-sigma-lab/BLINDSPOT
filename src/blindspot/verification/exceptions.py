"""Verification subsystem exceptions."""

from blindspot.exceptions import BenchmarkError


class VerificationError(BenchmarkError):
    """Base class for verification errors."""


class IntegrityError(VerificationError):
    """Raised when artifact integrity checks fail."""


class ReplayDivergenceError(VerificationError):
    """Raised when trajectory replay produces divergent state."""


class JudgeError(VerificationError):
    """Raised when a judge response is invalid."""


class AdjudicationError(VerificationError):
    """Raised when adjudication cannot resolve a conflict."""
