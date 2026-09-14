"""Pairwise generator — covers parameter interactions with fewer cases."""

from __future__ import annotations

import itertools
from typing import Any

from blindspot.scenario_generators.base import ScenarioGenerator
from blindspot.scenarios.templates import ScenarioTemplate


class PairwiseGenerator(ScenarioGenerator):
    """Generates pairwise-covering parameter combinations."""

    def generate(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        max_count: int | None = None,
    ) -> list[dict[str, Any]]:
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

        if len(enum_params) < 2:
            from blindspot.scenario_generators.cartesian import CartesianGenerator
            return CartesianGenerator().generate(template, seed, max_count)

        keys = sorted(enum_params.keys())
        results: list[dict[str, Any]] = []
        covered_pairs: set[tuple] = set()

        # Cover every pair of parameter values at least once
        for ki, kj in itertools.combinations(range(len(keys)), 2):
            kname_i, kname_j = keys[ki], keys[kj]
            for vi, vj in itertools.product(enum_params[kname_i], enum_params[kname_j]):
                pair_key = (kname_i, vi, kname_j, vj)
                if pair_key in covered_pairs:
                    continue
                params: dict[str, Any] = {}
                for k in keys:
                    if k == kname_i:
                        params[k] = vi
                    elif k == kname_j:
                        params[k] = vj
                    else:
                        params[k] = enum_params[k][0]
                params.update({k: v for k, v in fixed_params.items() if k not in params})
                errors = template.validate_parameters(params)
                if errors:
                    continue
                spec = template.instantiate(params, seed + len(results))
                results.append(spec)
                covered_pairs.add(pair_key)
                if max_count and len(results) >= max_count:
                    return results

        return results
