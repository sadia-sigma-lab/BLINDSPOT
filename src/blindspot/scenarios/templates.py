"""Scenario template loading and parameterization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from blindspot.scenarios.exceptions import ScenarioGenerationError


class TemplateParameter(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    param_type: str
    required: bool = True
    default: Any = None
    values: list[Any] | None = None
    description: str = ""


class ScenarioTemplate(BaseModel):
    """Parameterized template for generating scenario families."""

    model_config = ConfigDict(frozen=True)

    template_id: str
    display_name: str = ""
    description: str = ""
    parameters: list[TemplateParameter] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    base_spec: dict[str, Any] = Field(default_factory=dict)
    atom_ids: list[str] = Field(default_factory=list)

    def validate_parameters(self, params: dict[str, Any]) -> list[str]:
        """Return a list of validation error strings."""
        errors: list[str] = []
        for param in self.parameters:
            if param.required and param.name not in params:
                if param.default is None:
                    errors.append(f"Required parameter {param.name!r} is missing")
            if param.name in params and param.values is not None:
                if params[param.name] not in param.values:
                    errors.append(
                        f"Parameter {param.name!r}={params[param.name]!r} not in "
                        f"allowed values {param.values}"
                    )
        return errors

    def instantiate(self, params: dict[str, Any], seed: int = 42) -> dict[str, Any]:
        """Return a scenario dict with parameters substituted."""
        errors = self.validate_parameters(params)
        if errors:
            raise ScenarioGenerationError(
                f"Template {self.template_id!r} parameter errors: {'; '.join(errors)}"
            )

        # Fill defaults
        resolved: dict[str, Any] = {}
        for param in self.parameters:
            resolved[param.name] = params.get(param.name, param.default)

        # Deep-copy base spec and substitute
        spec = json.loads(json.dumps(self.base_spec, default=str))
        spec = _substitute(spec, resolved)
        spec["_template_id"] = self.template_id
        spec["_params"] = resolved
        spec["_seed"] = seed
        spec["_scenario_id"] = _stable_scenario_id(self.template_id, resolved, seed)
        return spec


def _substitute(obj: Any, params: dict[str, Any]) -> Any:
    if isinstance(obj, str):
        for k, v in params.items():
            obj = obj.replace(f"{{{{{k}}}}}", str(v) if v is not None else "")
        return obj
    if isinstance(obj, dict):
        return {k: _substitute(v, params) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute(item, params) for item in obj]
    return obj


def _stable_scenario_id(template_id: str, params: dict[str, Any], seed: int) -> str:
    key = json.dumps({"t": template_id, "p": params, "s": seed}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def load_template(path: Path) -> ScenarioTemplate:
    """Load a scenario template from a YAML file."""
    if not path.exists():
        raise ScenarioGenerationError(f"Template not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ScenarioGenerationError(f"Expected YAML mapping at {path}")
    return ScenarioTemplate(**raw)
