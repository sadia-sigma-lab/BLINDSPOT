# Tool Runtime

The `PythonTool.execute()` pipeline runs 19 steps in order:

1. Validate arguments (Pydantic model)
2. Idempotency check (return cached result if key matches)
3. Pre-authorization failure injection
4. Create scoped read-only view
5. Authorization (permissions + policies + approvals)
6. Pre-execution failure injection
7. Read phase (no side effects)
8. Mutation planning (no live mutations)
9. Write scope validation
10. Pre-commit failure injection
11. Atomic transaction commit
12. Post-commit failure injection (state already committed)
13. Event emission
14. Audit record emission
15. Response-only failure injection (false success)
16. Idempotency result storage
17. Return result

Concrete tools implement only `read()` and `plan_mutations()`. The pipeline is owned entirely by `PythonTool.execute()`.
