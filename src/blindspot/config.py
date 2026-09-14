"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from blindspot.exceptions import ConfigurationError
from blindspot.loaders.yaml_loader import load_yaml_file


class ProjectConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    artifact_root: str = "data"


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    seed: int = 42
    max_steps: int = 20
    strict_validation: bool = True


class PluginsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    modules: list[str] = []


class LoggingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    level: str = "INFO"
    json_logs: bool = False

    @field_validator("level")
    @classmethod
    def _valid_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Log level must be one of {valid}, got {v!r}")
        return upper


class StorageConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    backend: str = "filesystem"
    root: str = "data"


class BenchmarkConfig(BaseModel):
    """Fully resolved, immutable benchmark configuration."""

    model_config = ConfigDict(frozen=True)

    project: ProjectConfig
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


_ENV_OVERRIDES: dict[str, tuple[str, ...]] = {
    "LHBENCH_SEED": ("runtime", "seed"),
    "LHBENCH_MAX_STEPS": ("runtime", "max_steps"),
    "LHBENCH_LOG_LEVEL": ("logging", "level"),
    "LHBENCH_STORAGE_ROOT": ("storage", "root"),
    "LHBENCH_ARTIFACT_ROOT": ("project", "artifact_root"),
}


def _apply_env_overrides(raw: dict[str, Any]) -> dict[str, Any]:
    """Mutate raw config dict with environment variable overrides."""
    for env_var, path in _ENV_OVERRIDES.items():
        value = os.environ.get(env_var)
        if value is None:
            continue
        node = raw
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = value
    return raw


def load_config(path: str | Path) -> BenchmarkConfig:
    """Load, override, and validate a BenchmarkConfig from a YAML file."""
    raw = load_yaml_file(path)
    raw = _apply_env_overrides(raw)

    if "project" not in raw:
        raise ConfigurationError("Config missing required key 'project'")

    try:
        return BenchmarkConfig(**raw)
    except Exception as exc:
        raise ConfigurationError(f"Invalid configuration at {path}: {exc}") from exc
