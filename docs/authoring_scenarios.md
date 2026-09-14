# Authoring Scenarios

## Minimal scenario (Python)

```python
from blindspot.scenarios.schema import FullScenarioSpec
from blindspot.scenarios.registry import ScenarioRegistry

spec = FullScenarioSpec(
    metadata=ScenarioMetadata(
        scenario_id=ComponentID(namespace="my", name="scenario-001", version="1.0.0"),
        display_name="My Scenario", domain_id="core:minimal-workspace@1.0.0",
        fixture_id="core:minimal-workspace@1.0.0", source="hand_authored",
    ),
    initial_state=InitialStateSpec(fixture_id="core:minimal-workspace@1.0.0", seed=42),
    actors=[ScenarioActorSpec(actor_id="agent", actor_type="target_agent", visibility_profile="default")],
    task=BenignTaskSpec(task_id="t1", instruction="...", user_actor_id="agent",
                        target_actor_id="agent", goal_predicates=["done"]),
    tools=ToolBindingSpec(collection_id="core:minimal-workspace@1.0.0",
                          enabled_tool_ids=["list-files"]),
    outcomes=OutcomeSpec(benign_success_predicates=["done"]),
    horizon=HorizonProfile(max_interaction_steps=10, max_tool_calls=5),
    splits=ScenarioSplitMetadata(split="train", template_family="my:template"),
)

reg = ScenarioRegistry()
reg.register(spec)
```

## Key rules

- `actor_ids` must be unique
- `tools.enabled_tool_ids` and `tools.disabled_tool_ids` must not overlap
- Hidden grading state only in `hidden` section
- Every adversarial scenario must link a `clean_control_id`
