"""Safe YAML loading utilities (no arbitrary Python eval)."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import yaml

from blindspot.exceptions import ConfigurationError


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    p = Path(path)
    if not p.exists():
        raise ConfigurationError(f"YAML file not found: {p}")
    try:
        text = p.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Malformed YAML at {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Expected a YAML mapping at the root, got {type(data).__name__}")
    return data  # type: ignore[return-value]


def load_yaml_string(text: str) -> dict[str, Any]:
    """Parse a YAML string into a dict."""
    try:
        data = yaml.safe_load(io.StringIO(text))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Malformed YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Expected a YAML mapping, got {type(data).__name__}")
    return data  # type: ignore[return-value]
