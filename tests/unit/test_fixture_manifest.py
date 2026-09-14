"""Unit tests for fixture manifest loading and validation."""

import pytest
from pathlib import Path

from blindspot.data_model.manifest import load_manifest, FixtureManifest
from blindspot.exceptions import ConfigurationError


MANIFEST_PATH = Path("src/lh_agent_bench/domains/minimal_workspace/fixtures/manifest.yaml")


def test_valid_manifest_loads():
    m = load_manifest(MANIFEST_PATH)
    assert m.fixture_id == "core:minimal-workspace@1.0.0"
    assert len(m.files) > 0


def test_no_duplicate_collections(tmp_path):
    yaml_text = """
fixture_id: test:x@1.0.0
domain_id: test:x@1.0.0
schema_version: "1.0.0"
fixture_version: "1.0.0"
seed: 42
files:
  - path: a.json
    format: json
    collection: users
    visibility: private
  - path: b.json
    format: json
    collection: users
    visibility: private
"""
    p = tmp_path / "manifest.yaml"
    p.write_text(yaml_text)
    with pytest.raises(ConfigurationError):
        load_manifest(p)


def test_hidden_files_classified():
    m = load_manifest(MANIFEST_PATH)
    hidden = m.hidden_files()
    assert any(f.collection == "grading" for f in hidden)


def test_visible_files_excludes_hidden():
    m = load_manifest(MANIFEST_PATH)
    visible = m.visible_files()
    assert all(f.visibility != "hidden" for f in visible)


def test_missing_manifest_raises():
    with pytest.raises(ConfigurationError):
        load_manifest(Path("/nonexistent/manifest.yaml"))
