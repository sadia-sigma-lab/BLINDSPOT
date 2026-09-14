"""Load FullScenarioSpec from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from blindspot.scenarios.exceptions import ScenarioError
from blindspot.scenarios.schema import FullScenarioSpec


def load_full_scenario(path: Path) -> FullScenarioSpec:
    """Load and validate a FullScenarioSpec from a YAML file."""
    if not path.exists():
        raise ScenarioError(f"Scenario file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ScenarioError(f"Malformed YAML at {path}: {exc}") from exc
    try:
        return FullScenarioSpec(**raw)
    except ValidationError as exc:
        raise ScenarioError(f"Invalid scenario spec at {path}: {exc}") from exc
