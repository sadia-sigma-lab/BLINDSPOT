# Extension Points

## Add a Domain

1. Implement a class with `initial_state()`, `tools()`, and `build_observation()` methods.
2. Give it a `ComponentMetadata` with a unique `ComponentID`.
3. In a plugin's `register()`, call `registries.domains.register(domain.metadata.component_id.canonical(), domain)`.

## Add a Tool

1. Subclass `Tool` and implement `schema()` and `execute()`.
2. Declare `read_scopes` and `write_scopes`.
3. Register via `registries.tools.register(tool_id, tool)`.

## Add a Scenario

1. Write a YAML file following the `ScenarioSpec` schema.
2. Load with `load_scenario(path)` and register via `registries.scenarios.register(scenario_id, spec)`.

## Add an Evaluator

1. Subclass `Evaluator` and implement `evaluate()`.
2. Register via `registries.evaluators.register(eval_id, evaluator)`.

## Add an Actor

1. Subclass `Actor` and implement `act()`.
2. Register via `registries.actors.register(actor_id, actor)`.

## Add an Attack (future)

1. Implement a `RuntimeHooks` provider that injects behavior via `before_observation`, `after_tool`, or similar hooks.
2. Register the attack in the attacks registry.
3. Attach it to an engine instance before episode start.

## Add an Intervention (future)

1. Implement an intervention that monitors state or actions and modifies them.
2. Register via `registries.interventions.register(...)`.
3. Wire into `RuntimeHooks.before_action` or `after_tool`.
