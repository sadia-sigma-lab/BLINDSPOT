"""Initial state definition for the minimal workspace domain."""

from typing import Any


def initial_state_dict() -> dict[str, Any]:
    """Return the canonical initial state for the minimal workspace scenario."""
    return {
        "users": {
            "user_1": {"name": "Alice", "role": "employee"},
        },
        "files": {
            "file_1": {
                "name": "report.txt",
                "owner_id": "user_1",
                "content": "Quarterly report",
                "shared_with": [],
            }
        },
    }
