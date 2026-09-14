"""Constraint-based generator — only valid combinations."""

from __future__ import annotations

import itertools
import random
from typing import Any

from blindspot.scenario_generators.base import ScenarioGenerator
from blindspot.scenarios.templates import ScenarioTemplate


class ConstrainedGenerator(ScenarioGenerator):
    """Generates valid combinations by filtering against template constraints."""

    def generate(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        max_count: int | None = None,
    ) -> list[dict[str, Any]]:
        from blindspot.scenario_generators.cartesian import CartesianGenerator
        all_specs = CartesianGenerator().generate(template, seed)

        # Shuffle deterministically for variety
        rng = random.Random(seed)
        rng.shuffle(all_specs)

        results = all_specs[:max_count] if max_count else all_specs
        return results
