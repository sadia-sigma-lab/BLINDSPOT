# Raw Trajectory Format

## `trajectory.jsonl` fields (per step)

- `run_id`, `episode_id`, `scenario_id`, `session_id`
- `step`, `global_step`, `acting_actor_id`
- `observation` — messages at this step
- `prompt_artifact` — rendered messages, template IDs, source hashes
- `raw_model_response` — provider response (if `persist_raw_responses=True`)
- `parse_result` — success, action, repair info
- `selected_action` — final parsed AgentAction
- `tool_execution_result` — agent-visible tool output
- `pre_state_hash`, `post_state_hash` — SHA-256 of `world_state.public`
- `token_usage`, `latency_ms`
- `attack_trace_refs`, `events_processed`

## Immutability

`trajectory.jsonl` is append-only. No step is ever overwritten.
Raw provider responses are stored separately in `provider_responses.jsonl`.
`final_state.json` and `final_state_hash.txt` record the terminal world state.
