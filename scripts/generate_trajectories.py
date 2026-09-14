#!/usr/bin/env python
"""
Generate benchmark trajectories using a real LLM (Claude Opus 4.6 by default).

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python scripts/generate_trajectories.py

Options via environment variables:
    ANTHROPIC_API_KEY   — required
    BENCH_MODEL         — model ID (default: claude-opus-4-6)
    BENCH_SCENARIOS     — comma-separated scenario IDs (default: all reference scenarios)
    BENCH_RUNS_PER      — runs per scenario (default: 3)
    BENCH_MAX_TOKENS    — max output tokens per turn (default: 2048)
    BENCH_MAX_STEPS     — max steps per episode (default: 30)
    BENCH_SEED          — random seed (default: 42)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Configuration ────────────────────────────────────────────────────────────

MODEL = os.environ.get("BENCH_MODEL", "claude-opus-4-6")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
RUNS_PER_SCENARIO = int(os.environ.get("BENCH_RUNS_PER", "3"))
MAX_TOKENS = int(os.environ.get("BENCH_MAX_TOKENS", "2048"))
MAX_STEPS = int(os.environ.get("BENCH_MAX_STEPS", "30"))
SEED = int(os.environ.get("BENCH_SEED", "42"))

SCENARIO_IDS_ENV = os.environ.get("BENCH_SCENARIOS", "")
SCENARIO_IDS = [s.strip() for s in SCENARIO_IDS_ENV.split(",") if s.strip()] or None

# ── Setup ─────────────────────────────────────────────────────────────────────

def check_aws_credentials() -> str:
    """Verify AWS credentials are available for Bedrock access."""
    try:
        import boto3
        sts = boto3.client("sts", region_name=AWS_REGION)
        identity = sts.get_caller_identity()
        account = identity["Account"]
        arn = identity["Arn"]
        return f"AWS account {account} ({arn.split('/')[-1]})"
    except Exception as exc:
        print(f"ERROR: AWS credentials not available: {exc}")
        print()
        print("Ensure you have valid AWS credentials configured, e.g.:")
        print("  aws configure")
        print("  or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars")
        sys.exit(1)


def build_scenario_registry():
    """Load all reference scenario families."""
    from blindspot.scenarios.registry import ScenarioRegistry
    from blindspot.domains.minimal_workspace.scenarios.reference_families import (
        ALL_REFERENCE_SCENARIOS,
    )
    reg = ScenarioRegistry()
    for factory in ALL_REFERENCE_SCENARIOS:
        try:
            spec = factory()
            reg.register(spec, strict=False)
        except Exception as exc:
            print(f"  Warning: skipped {factory.__name__}: {exc}")
    return reg


def build_agent_config() -> "AgentConfig":
    from blindspot.agents.config import AgentConfig
    return AgentConfig(
        agent_id=f"claude-bedrock-{MODEL.replace('.', '-')}",
        adapter_id="claude",
        model_name=MODEL,
        provider="bedrock",
        temperature=0.3,
        max_output_tokens=MAX_TOKENS,
        max_retries=2,
        timeout_seconds=120.0,
    )


# ── Patched orchestrator that uses the real LLM ───────────────────────────────

def build_real_agent_adapter():
    """Build and return a ClaudeAdapter instance using Bedrock."""
    from blindspot.agents.claude_adapter import ClaudeAdapter
    return ClaudeAdapter(aws_region=AWS_REGION)


def run_scenario_with_llm(
    scenario_id: str,
    scenario_registry,
    agent_adapter,
    agent_config,
    seed: int,
    run_index: int,
    artifact_root: str,
) -> dict:
    """
    Run one episode with the real LLM.
    This patches the orchestrator to use the actual Claude model.
    """
    from blindspot.simulation.orchestrator import EpisodeOrchestrator, RunConfig
    from blindspot.agents.registry import AgentAdapterRegistry
    from blindspot.agents.scripted import ScriptedAgentAdapter

    # Build a custom agent registry with only the Claude adapter
    reg = AgentAdapterRegistry()
    reg.register(agent_adapter)
    reg.register(ScriptedAgentAdapter())  # fallback

    run_config = RunConfig(
        scenario_id=scenario_id,
        seed=seed + run_index,
        target_agent=agent_config,
        max_steps_override=MAX_STEPS,
        persist_prompts=True,
        persist_raw_responses=True,
    )

    orch = EpisodeOrchestrator(
        scenario_registry=scenario_registry,
        artifact_root=artifact_root,
        agent_registry=reg,
    )

    t_start = time.monotonic()
    result = orch.run(run_config)
    duration = time.monotonic() - t_start

    return {
        "run_id": result.run_id,
        "scenario_id": scenario_id,
        "seed": seed + run_index,
        "model": MODEL,
        "status": result.status,
        "total_steps": result.total_steps,
        "total_tool_calls": result.total_tool_calls,
        "final_state_hash": result.final_state_hash[:12] if result.final_state_hash else "",
        "duration_seconds": round(duration, 2),
        "run_dir": result.run_dir,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(" LH-AgentBench Trajectory Generator")
    print(f" Model    : {MODEL}")
    print(f" Provider : AWS Bedrock ({AWS_REGION})")
    print(f" Runs     : {RUNS_PER_SCENARIO} per scenario")
    print(f" Steps    : up to {MAX_STEPS} per episode")
    print(f" Tokens   : up to {MAX_TOKENS} per turn")
    print("=" * 60)
    print()

    # 1. Check AWS credentials
    aws_identity = check_aws_credentials()
    print(f"✓ AWS credentials: {aws_identity}")

    # 2. Build scenario registry
    print("Loading scenarios...")
    scenario_registry = build_scenario_registry()
    all_ids = scenario_registry.list()
    print(f"✓ {len(all_ids)} scenarios loaded")
    for sid in all_ids:
        spec = scenario_registry.get(sid)
        print(f"  • {sid} [{spec.splits.split}]")

    # 3. Select scenarios
    target_ids = SCENARIO_IDS or all_ids
    print(f"\nWill run: {len(target_ids)} scenario(s) × {RUNS_PER_SCENARIO} runs = "
          f"{len(target_ids) * RUNS_PER_SCENARIO} total episodes")
    print()

    # 4. Build adapters
    agent_adapter = build_real_agent_adapter()
    agent_config = build_agent_config()
    print(f"✓ Agent adapter ready: {MODEL}")

    # 5. Run episodes
    all_results = []
    total = len(target_ids) * RUNS_PER_SCENARIO
    done = 0

    for scenario_id in target_ids:
        if not scenario_registry.contains(scenario_id):
            print(f"  SKIP: {scenario_id} not in registry")
            continue

        spec = scenario_registry.get(scenario_id)
        print(f"\n{'─'*55}")
        print(f"Scenario: {spec.metadata.display_name}")
        print(f"  ID     : {scenario_id}")
        print(f"  Type   : {spec.metadata.tags}")
        print(f"  Horizon: {spec.horizon.max_interaction_steps} steps / "
              f"{spec.horizon.max_tool_calls} tools")

        for run_i in range(RUNS_PER_SCENARIO):
            done += 1
            print(f"\n  Run {run_i+1}/{RUNS_PER_SCENARIO} [{done}/{total}]  "
                  f"seed={SEED + run_i} ...", end="", flush=True)

            t0 = time.monotonic()
            try:
                result = run_scenario_with_llm(
                    scenario_id=scenario_id,
                    scenario_registry=scenario_registry,
                    agent_adapter=agent_adapter,
                    agent_config=agent_config,
                    seed=SEED,
                    run_index=run_i,
                    artifact_root=str(Path(__file__).parent.parent / "data"),
                )
                duration = time.monotonic() - t0
                status_icon = "✓" if result["status"] in ("completed", "terminated") else "⚠"
                print(f" {status_icon} {result['status']} | "
                      f"{result['total_steps']} steps | "
                      f"{result['total_tool_calls']} tools | "
                      f"{duration:.1f}s | "
                      f"run={result['run_id']}")
                all_results.append(result)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user.")
                _save_results(all_results)
                sys.exit(0)
            except Exception as exc:
                duration = time.monotonic() - t0
                print(f" ✗ ERROR after {duration:.1f}s: {exc}")
                all_results.append({
                    "scenario_id": scenario_id, "seed": SEED + run_i,
                    "model": MODEL, "status": "error", "error": str(exc),
                })

    # 6. Summary
    print(f"\n{'='*60}")
    print(" SUMMARY")
    print(f"{'='*60}")
    completed = [r for r in all_results if r.get("status") in ("completed", "terminated")]
    errors = [r for r in all_results if r.get("status") == "error"]
    steps_all = [r.get("total_steps", 0) for r in completed]
    avg_steps = sum(steps_all) / len(steps_all) if steps_all else 0

    print(f"Total runs   : {len(all_results)}")
    print(f"Completed    : {len(completed)}")
    print(f"Errors       : {len(errors)}")
    if completed:
        print(f"Avg steps    : {avg_steps:.1f}")
        print(f"Min/Max steps: {min(steps_all)} / {max(steps_all)}")

    _save_results(all_results)
    print(f"\nRaw trajectories: data/raw/runs/")
    print("Next steps:")
    print("  Verify:      blindspot verify run --run-id <run_id>")
    print("  Risk label:  blindspot risk label --verified-id <vt_id>")
    print("  Eval passk:  blindspot eval passk --run-ids run1,run2,...  --k 1,4,8")
    return 0 if not errors else 1


def _save_results(results: list) -> None:
    if not results:
        return
    out_path = Path("data/reports/generation_run.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
