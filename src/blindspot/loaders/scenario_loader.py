"""Load and validate ScenarioSpec from YAML files."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from blindspot.core.identifiers import ComponentID
from blindspot.core.scenario import ScenarioSpec
from blindspot.exceptions import ScenarioNotFoundError
from blindspot.loaders.yaml_loader import load_yaml_file


def load_scenario(path: str | Path) -> ScenarioSpec:
    """Parse a scenario YAML file into a ScenarioSpec."""
    try:
        raw = load_yaml_file(path)
    except Exception as exc:
        raise ScenarioNotFoundError(f"Cannot load scenario from {path}: {exc}") from exc

    # Expand nested ID dicts
    for id_field in ("scenario_id", "domain_id"):
        if id_field in raw and isinstance(raw[id_field], dict):
            raw[id_field] = ComponentID(**raw[id_field])

    try:
        return ScenarioSpec(**raw)
    except ValidationError as exc:
        raise ScenarioNotFoundError(f"Invalid scenario spec at {path}: {exc}") from exc
