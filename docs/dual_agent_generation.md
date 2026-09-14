# Dual-Agent Multi-Turn Data Generation

BLINDSPOT generates trajectories using a dual-agent loop with three interacting components: a **UserAgent** (drives the conversation), a **TargetAgent** (the AI assistant being evaluated), and a **Judge** (evaluates the trajectory).

## Architecture

| Agent | Role |
|-------|------|
| UserAgent | Drives user/attacker turns using a family-specific prompt template |
| TargetAgent | AI assistant under test — uses scenario tools and follows active policies |
| Judge | Evaluates the completed trajectory and assigns a trajectory-level outcome |

## The tool round-trip fix

The critical fix in `ConversationHistory`:

**Broken**: tool results fed as `[Tool result]: ...` plain text → agent ignores → loops  
**Fixed**: tool results fed as `{"type": "tool_result", "tool_use_id": ..., "content": ...}` blocks → agent sees real results → reasons and progresses

## Running

```bash
# Full run (all scenarios, 3 runs each)
python scripts/generate_trajectories.py

# Single scenario
BENCH_SCENARIOS="workspace:clean-external-sharing-001@1.0.0" \
BENCH_RUNS_PER=1 \
python scripts/generate_trajectories.py

# Custom models via environment variables
BENCH_USER_MODEL=<user-agent-model-id> \
BENCH_EXEC_MODEL=<execution-agent-model-id> \
BENCH_JUDGE_MODEL=<judge-model-id> \
python scripts/generate_trajectories.py
```

## Output

- `data/raw/runs/<run_id>/` — raw trajectory artifacts
- `data/datasets/train.jsonl` + `validation.jsonl` + `test.jsonl` — curated splits

## Expected trajectory characteristics

| Characteristic | Typical value |
|----------------|--------------|
| Average turns | 8–20 per episode |
| Average tool calls | 5–20 per episode |
| Attack families | 22 families with distinct escalation strategies |
| Tool results | Propagate correctly via structured tool_result blocks |

## Adaptive adversary

For user-driven attack families, the UserAgent generates each message conditioned on the TargetAgent's preceding response — the adversary adapts to refusals, clarification requests, and partial compliance. See `prompts/attacker_simulator/` for per-family prompt templates and `src/blindspot/dual_agent/personas.py` for template selection logic.
