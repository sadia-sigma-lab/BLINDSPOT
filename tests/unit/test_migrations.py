"""Unit tests for the migration framework."""

import pytest

from blindspot.data_model.migrations import MigrationRegistry, SchemaMigration, MigrationError
from blindspot.domains.minimal_workspace.migrations.v1_0_0_to_v1_1_0 import WorkspaceV100ToV110


def test_migration_path_found():
    reg = MigrationRegistry()
    reg.register(WorkspaceV100ToV110())
    path = reg.find_path("1.0.0", "1.1.0")
    assert len(path) == 1
    assert path[0].target_version == "1.1.0"


def test_migration_output_validates():
    migration = WorkspaceV100ToV110()
    source = {
        "resources": {
            "file_1": {"name": "report.txt", "schema_version": "1.0.0"}
        }
    }
    result = migration.migrate(source)
    assert result["resources"]["file_1"]["content_type"] == "text/plain"
    assert result["resources"]["file_1"]["schema_version"] == "1.1.0"


def test_source_remains_unchanged():
    migration = WorkspaceV100ToV110()
    source = {"resources": {"f": {"schema_version": "1.0.0"}}}
    migration.migrate(source)
    # source must not be modified
    assert "content_type" not in source["resources"]["f"]


def test_missing_migration_path_fails():
    reg = MigrationRegistry()
    with pytest.raises(MigrationError):
        reg.find_path("1.0.0", "9.9.9")


def test_same_version_path_is_empty():
    reg = MigrationRegistry()
    assert reg.find_path("1.0.0", "1.0.0") == []


def test_downgrade_raises():
    migration = WorkspaceV100ToV110()
    with pytest.raises(MigrationError):
        migration.downgrade({})


def test_multi_hop_migration():
    class AtoB(SchemaMigration):
        source_version = "1.0"
        target_version = "1.1"
        def migrate(self, data):
            return {**data, "step": "A->B"}

    class BtoC(SchemaMigration):
        source_version = "1.1"
        target_version = "1.2"
        def migrate(self, data):
            return {**data, "step2": "B->C"}

    reg = MigrationRegistry()
    reg.register(AtoB())
    reg.register(BtoC())
    result = reg.apply_path({}, "1.0", "1.2")
    assert result["step"] == "A->B"
    assert result["step2"] == "B->C"
