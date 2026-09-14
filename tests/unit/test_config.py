"""Unit tests for configuration loading."""

import os
from pathlib import Path

import pytest

from blindspot.config import load_config
from blindspot.exceptions import ConfigurationError


def test_valid_config(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bench.yaml"
    cfg_file.write_text(
        "project:\n  name: test\n  artifact_root: data\n"
        "runtime:\n  seed: 7\n",
        encoding="utf-8",
    )
    cfg = load_config(cfg_file)
    assert cfg.project.name == "test"
    assert cfg.runtime.seed == 7


def test_missing_project_key_raises(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bad.yaml"
    cfg_file.write_text("runtime:\n  seed: 1\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(cfg_file)


def test_env_override_seed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg_file = tmp_path / "bench.yaml"
    cfg_file.write_text("project:\n  name: test\n", encoding="utf-8")
    monkeypatch.setenv("LHBENCH_SEED", "99")
    cfg = load_config(cfg_file)
    assert cfg.runtime.seed == 99


def test_malformed_plugin_path_is_recorded(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bench.yaml"
    cfg_file.write_text(
        "project:\n  name: test\nplugins:\n  modules:\n    - bad.module.NoClass\n",
        encoding="utf-8",
    )
    cfg = load_config(cfg_file)
    assert "bad.module.NoClass" in cfg.plugins.modules
