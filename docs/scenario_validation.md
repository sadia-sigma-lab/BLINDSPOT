# Scenario Validation

## Checks performed

- Unique actor IDs
- Task actor references valid actors
- Tool binding has no conflicts
- Attack bindings reference known attacks (when registry provided)
- Horizon values positive and consistent
- Adversarial scenarios have clean control links
- Task has goal predicates or safe alternatives

## Solvability checks

- Required tools (`list-files`, `read-file`) are enabled
- Horizon is not obviously too short for expected subgoals

## Registry enforcement

`ScenarioRegistry.register(spec, strict=True)` rejects scenarios with validation errors.
