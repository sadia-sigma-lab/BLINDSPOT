# Testing Tools

## Unit test pattern

```python
def test_my_tool(tmp_state, deps, ctx):
    tool = MyTool()
    new_state, result = tool.execute(tmp_state, {"file_id": "f1"}, ctx, deps)
    assert result.success
    assert "f1" in new_state.public["resources"]
```

## Integration test helpers

- `load_workspace_state()` — returns a WorldState from the fixture bundle
- `build_default_dependencies()` — no failure profiles, in-memory audit/idempotency
- `make_context(actor_id, step, seed)` — creates a ToolExecutionContext

## Hidden state check

```python
assert result.internal_truth == {}  # no internal truth in normal success
assert "grading" not in str(result.agent_visible())
```
