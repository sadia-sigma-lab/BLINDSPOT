"""Schema migration framework."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from blindspot.exceptions import BenchmarkError


class MigrationError(BenchmarkError):
    """Raised when a migration fails or a path cannot be found."""


class SchemaMigration(ABC):
    """Abstract migration from one schema version to the next."""

    source_version: str
    target_version: str

    @abstractmethod
    def migrate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data from source_version to target_version.

        Must return a NEW dict — never modify the input in place.
        """
        ...

    def downgrade(self, data: dict[str, Any]) -> dict[str, Any]:
        raise MigrationError(
            f"Downgrade from {self.target_version} to {self.source_version} is not supported"
        )


class MigrationRegistry:
    """Registry of available schema migrations."""

    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], SchemaMigration] = {}

    def register(self, migration: SchemaMigration) -> None:
        key = (migration.source_version, migration.target_version)
        if key in self._migrations:
            raise MigrationError(
                f"Migration {migration.source_version} -> {migration.target_version} "
                "is already registered"
            )
        self._migrations[key] = migration

    def find_path(self, source: str, target: str) -> list[SchemaMigration]:
        """Return an ordered list of migrations from source to target version.

        Uses BFS to find the shortest registered path.
        """
        if source == target:
            return []

        from collections import deque

        queue: deque[tuple[str, list[SchemaMigration]]] = deque()
        queue.append((source, []))
        visited: set[str] = {source}

        while queue:
            current, path = queue.popleft()
            for (src, tgt), migration in self._migrations.items():
                if src == current and tgt not in visited:
                    new_path = path + [migration]
                    if tgt == target:
                        return new_path
                    visited.add(tgt)
                    queue.append((tgt, new_path))

        raise MigrationError(
            f"No migration path found from {source!r} to {target!r}"
        )

    def apply_path(
        self, data: dict[str, Any], source: str, target: str
    ) -> dict[str, Any]:
        """Apply the found migration path and return the transformed data."""
        path = self.find_path(source, target)
        result = data
        for migration in path:
            result = migration.migrate(result)
        return result


# Module-level default registry (not a singleton — create instances per use)
def make_migration_registry() -> MigrationRegistry:
    return MigrationRegistry()
