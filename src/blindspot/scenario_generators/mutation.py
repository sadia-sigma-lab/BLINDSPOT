"""Mutation generator — creates controlled variants of existing scenarios."""

from __future__ import annotations

import copy
import hashlib
import json
import random
from typing import Any

from blindspot.scenario_generators.base import ScenarioGenerator
from blindspot.scenarios.templates import ScenarioTemplate


class MutationGenerator(ScenarioGenerator):
    """Creates variants by applying controlled mutations to a base scenario."""

    MUTATION_AXES = [
        "actor", "resource", "policy", "approval",
        "attack_source", "attack_timing", "horizon", "tool_availability",
    ]

    def __init__(self, base_params: dict[str, Any] | None = None) -> None:
        self._base_params = base_params or {}

    def generate(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        max_count: int | None = None,
    ) -> list[dict[str, Any]]:
        rng = random.Random(seed)
        results: list[dict[str, Any]] = []
        base = copy.deepcopy(self._base_params)

        for i, axis in enumerate(self.MUTATION_AXES):
            if max_count and len(results) >= max_count:
                break
            mutated = copy.deepcopy(base)
            mutated[f"_mutation_axis"] = axis
            mutated[f"_mutation_seed"] = seed + i
            # Apply simple mutations
            if axis == "horizon":
                current = mutated.get("max_steps", 20)
                mutated["max_steps"] = max(5, current + rng.randint(-5, 10))
            elif axis == "approval":
                mutated["requires_approval"] = not mutated.get("requires_approval", True)

            errors = template.validate_parameters(mutated)
            if errors:
                continue

            try:
                spec = template.instantiate(mutated, seed + i)
                spec["_mutation_axis"] = axis
                spec["_parent_seed"] = seed
                results.append(spec)
            except Exception:
                continue

        return results
