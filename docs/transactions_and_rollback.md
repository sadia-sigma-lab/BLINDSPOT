# Transactions and Rollback

## Transaction

`TransactionManager.commit(state, plan, write_scopes)` stages mutations on a deep copy, validates scopes, commits atomically, and returns a `TransactionResult` with a normalized `StateDiff`.

A failed validation leaves `state` unchanged.

## Rollback

When `ToolSpecification.reversible=True`, the runtime issues a one-time `rollback_token`. Call `RollbackManager.rollback(state, token, actor_id, ctx)` to restore the pre-mutation state.

Rollback constraints:
- Token is one-time use
- Only the original actor may roll back (unless extended)
- Original audit records are preserved; a new audit record is added for the rollback
