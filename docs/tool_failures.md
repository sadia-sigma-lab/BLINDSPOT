# Tool Failures

## ToolFailureProfile

Configures deterministic failure injection keyed by `(tool_id, stage, seed, step)`.

Stages: `before_authorization`, `before_execution`, `before_commit`, `after_commit`, `response_only`

After-commit failures: state is committed but the agent sees an error. `internal_truth.committed=True` records the actual outcome for verifiers.

False success (`response_only` + `false_success`): agent sees failure, state is committed.

## Usage

```python
from blindspot.tools.failure_model import ToolFailureModel, ToolFailureProfile
deps.failure_model = ToolFailureModel([
    ToolFailureProfile(profile_id="sim", failure_probability=0.1,
                       failure_stage="before_execution", failure_type="transient_error")
])
```
