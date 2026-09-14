"""Shared helpers for workspace tools."""

from __future__ import annotations

from typing import Any

from blindspot.core.identifiers import ComponentID
from blindspot.core.metadata import ComponentMetadata
from blindspot.tools.state_view import ReadOnlyStateView


def _meta(name: str, description: str, version: str = "1.0.0") -> ComponentMetadata:
    return ComponentMetadata(
        component_id=ComponentID(namespace="core", name=name, version=version),
        display_name=name.replace("-", " ").title(),
        description=description,
        source_package="blindspot.domains.minimal_workspace.tools",
    )


def _file_visible(file_record: dict[str, Any], actor_id: str, permissions: dict) -> bool:
    """Return True if the actor can see this file (owner or has any permission)."""
    if file_record.get("owner_id") == actor_id:
        return True
    for perm in permissions.values():
        if isinstance(perm, dict):
            if perm.get("subject_id") == actor_id and perm.get("resource_id") == file_record.get("entity_id", ""):
                return True
    return True  # Simplified: all files visible in listing; read_file enforces access
