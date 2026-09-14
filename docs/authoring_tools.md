# Authoring Tools

## Class-based approach

```python
class MyTool(PythonTool[MyArgs, MyOutput]):
    specification = ToolSpecification(
        tool_id=ComponentID(namespace="core", name="my-tool", version="1.0.0"),
        description="...", read_scopes=["resources"], write_scopes=["resources"],
        side_effect_level="medium", requires_approval=True, approval_action="my-action",
        reversible=True, idempotent=True,
    )
    args_model = MyArgs
    output_model = MyOutput

    def read(self, view, args, context): ...
    def plan_mutations(self, view, args, context) -> MutationPlan: ...
```

## Decorator approach (read-only tools)

```python
@tool(tool_id="core:my-read@1.0.0", args_model=MyArgs, ...)
def my_read(view, args, context): ...
```

## Key rules

- `read()` must not mutate state
- `plan_mutations()` returns a `MutationPlan` — the engine commits it atomically
- Write scopes must be declared; undeclared writes are blocked before commit
