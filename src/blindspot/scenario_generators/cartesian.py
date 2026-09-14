"""Cartesian product generator — exhaustive coverage of small parameter spaces."""

from __future__ import annotations

import itertools
from typing import Any

from blindspot.scenario_generators.base import ScenarioGenerator
from blindspot.scenarios.templates import ScenarioTemplate


class CartesianGenerator(ScenarioGenerator):
    """Generates all valid combinations of enumerable parameters."""

    def generate(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        max_count: int | None = None,
    ) -> list[dict[str, Any]]:
        # Collect parameters with explicit value lists
        enum_params = {
            p.name: p.values
            for p in template.parameters
            if p.values is not None
        }
        fixed_params = {
            p.name: p.default
            for p in template.parameters
            if p.values is None and p.default is not None
        }

        if not enum_params:
            # Only fixed params — single scenario
            params = dict(fixed_params)
            errors = template.validate_parameters(params)
            if not errors:
                spec = template.instantiate(params, seed)
                return [spec]
            return []

        keys = sorted(enum_params.keys())  # deterministic ordering
        value_lists = [enum_params[k] for k in keys]
        results: list[dict[str, Any]] = []

        for combo in itertools.product(*value_lists):
            params = dict(zip(keys, combo))
            params.update(fixed_params)
            errors = template.validate_parameters(params)
            if errors:
                continue
            spec = template.instantiate(params, seed + len(results))
            results.append(spec)
            if max_count and len(results) >= max_count:
                break

        return results
