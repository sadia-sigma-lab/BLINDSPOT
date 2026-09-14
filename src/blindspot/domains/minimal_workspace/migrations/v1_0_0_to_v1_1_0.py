"""Migration: workspace schema v1.0.0 → v1.1.0.

Adds content_type field to file records (defaults to 'text/plain').
"""

from __future__ import annotations

import copy
from typing import Any

from blindspot.data_model.migrations import SchemaMigration


class WorkspaceV100ToV110(SchemaMigration):
    """Migrate workspace file records from v1.0.0 to v1.1.0."""

    source_version = "1.0.0"
    target_version = "1.1.0"

    def migrate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Add content_type='text/plain' to any file record missing it."""
        result = copy.deepcopy(data)
        if "resources" in result:
            for file_id, file_record in result["resources"].items():
                if isinstance(file_record, dict):
                    file_record.setdefault("content_type", "text/plain")
                    file_record["schema_version"] = "1.1.0"
        return result
