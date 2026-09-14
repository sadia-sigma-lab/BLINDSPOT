"""State hash utilities for trajectory verification."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_state_public(public: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(public, sort_keys=True, default=str).encode()
    ).hexdigest()
