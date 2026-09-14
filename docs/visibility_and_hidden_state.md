# Visibility and Hidden State

## Guarantees

- `WorldState.hidden` is never returned by `StateProjector`
- Hidden fixture files (under `hidden/`) go to `DomainStateBundle.hidden_data`
- `DomainStateBundle.hidden_data` is never placed into `WorldState.public`
- `VisibilityPolicy.hidden_collections` excludes collections from projections

## StateProjector

```python
projector = StateProjector()
projection = projector.project(state, actor_id="agent", policy=policy)
# projection["hidden"] is always {}
```

## Testing Hidden State

The integration test `test_fixture_determinism.py::test_hidden_grading_inaccessible_from_agent_view` verifies this guarantee end-to-end.
