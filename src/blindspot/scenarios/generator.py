"""High-level scenario generation pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from blindspot.scenario_generators.cartesian import CartesianGenerator
from blindspot.scenario_generators.mutation import MutationGenerator
from blindspot.scenarios.templates import ScenarioTemplate, load_template
from blindspot.scenarios.controls import generate_safe_twin


class ScenarioGenerationPipeline:
    """Orchestrates template loading, generation, twin creation, and storage."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_template(
        self,
        template: ScenarioTemplate,
        seed: int = 42,
        strategy: str = "cartesian",
        max_count: int | None = None,
        generate_twins: bool = True,
    ) -> list[dict[str, Any]]:
        """Generate scenarios and optionally safe twins."""
        if strategy == "cartesian":
            generator = CartesianGenerator()
        elif strategy == "mutation":
            generator = MutationGenerator()
        else:
            generator = CartesianGenerator()

        specs = generator.generate(template, seed=seed, max_count=max_count)

        result = []
        for spec in specs:
            result.append(spec)

            if generate_twins:
                twin_spec, twin_meta = generate_safe_twin(spec, "remove_payload")
                result.append(twin_spec)

        # Persist to output_dir
        for i, spec in enumerate(result):
            sid = spec.get("_scenario_id", f"scenario_{i:04d}")
            out_path = self._output_dir / f"{sid}.json"
            out_path.write_text(json.dumps(spec, indent=2, default=str), encoding="utf-8")

        return result
