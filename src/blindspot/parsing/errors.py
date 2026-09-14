"""Parse error types."""

from __future__ import annotations

from blindspot.exceptions import BenchmarkError


class ParseError(BenchmarkError):
    """Raised when action parsing fails irrecoverably."""
