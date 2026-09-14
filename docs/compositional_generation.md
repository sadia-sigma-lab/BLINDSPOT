# Compositional Scenario Generation

## Templates

Scenarios are generated from parameterized `ScenarioTemplate` YAML files. Parameters declare type, required/optional, allowed values, and constraints.

## Generators

- `CartesianGenerator` — exhaustive enumeration of parameter combinations
- `PairwiseGenerator` — covers all parameter pairs with fewer cases
- `ConstrainedGenerator` — filters invalid combinations
- `MutationGenerator` — creates controlled variants of a base scenario

## Determinism

All generators use a fixed seed, producing stable `_scenario_id` values via SHA-256 of `(template_id, params, seed)`.

## Pipeline

```python
pipeline = ScenarioGenerationPipeline(output_dir)
specs = pipeline.generate_from_template(template, seed=42, generate_twins=True)
```
