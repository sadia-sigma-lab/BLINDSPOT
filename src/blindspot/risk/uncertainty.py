"""Label uncertainty handling."""

from __future__ import annotations

from typing import Literal


def label_with_uncertainty(
    value: bool | None,
    confidence: float,
    mode: Literal["binary", "three_way", "probabilistic"],
) -> bool | None | float:
    """
    Apply uncertainty mode to a label.

    - binary: preserve True/False, map uncertain to False
    - three_way: preserve True/False/None (None = ambiguous)
    - probabilistic: return float (confidence × int(value) when known)
    """
    if mode == "binary":
        return bool(value) if value is not None else False
    if mode == "three_way":
        return value  # preserve None as ambiguous
    # probabilistic
    if value is None:
        return None
    return confidence * float(value)
