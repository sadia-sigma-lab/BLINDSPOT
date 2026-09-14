# Scopes and Visibility

## Read scopes

Declared in `ToolSpecification.read_scopes`. The `ReadOnlyStateView` enforces these — accessing an undeclared collection raises `ScopeViolationError`.

Collections in `_ALWAYS_HIDDEN` (`hidden`, `grading`, `attack_state`) are never accessible regardless of declared scopes.

## Write scopes

Declared in `ToolSpecification.write_scopes`. The `TransactionManager` rejects any operation targeting a collection not in the declared write scopes before committing.

## Hidden state guarantee

The `StateProjector` removes all hidden data from agent-visible projections. The `internal_truth` field in `ToolExecutionResult` is stripped by `agent_visible()`.
