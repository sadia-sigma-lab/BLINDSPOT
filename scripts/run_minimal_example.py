#!/usr/bin/env python
"""Run the minimal workspace example end-to-end"""

import sys
import uuid
from pathlib import Path

# Make src/ and project root importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from blindspot.core.action import AgentAction
from blindspot.loaders.plugin_loader import load_plugins
from blindspot.loaders.scenario_loader import load_scenario
from blindspot.registry import RegistryHub
from blindspot.runtime.engine import BenchmarkEngine
from blindspot.runtime.replay import replay_trajectory
from blindspot.storage.file_store import FileStore
from blindspot.storage.trajectory_store import TrajectoryStore


def main() -> int:
    print("=== Minimal Domain Example ===\n")

    hub = RegistryHub()
    load_plugins(
        [
            "blindspot.plugins.builtins:BuiltinPlugin",
            "examples.minimal_domain:MinimalDomainPlugin",
        ],
        hub,
    )

    scenario = load_scenario(Path("examples/minimal_domain/scenario.yaml"))
    print(f"Scenario: {scenario.scenario_id.canonical()}")
    print(f"Domain  : {scenario.domain_id.canonical()}\n")

    engine = BenchmarkEngine(hub)
    obs, info = engine.reset(scenario, seed=42)
    initial_state = engine.get_session().state.model_copy_deep()
    print(f"Episode : {info['episode_id']}")

    actions = [
        AgentAction(action_id=str(uuid.uuid4()), action_type="tool_call", name="list-files", arguments={}),
        AgentAction(action_id=str(uuid.uuid4()), action_type="tool_call", name="read-file", arguments={"file_id": "file_1"}),
        AgentAction(action_id=str(uuid.uuid4()), action_type="tool_call", name="share-file", arguments={"file_id": "file_1", "recipient": "auditor@example.org"}),
        AgentAction(action_id=str(uuid.uuid4()), action_type="message", content="Shared report.txt with auditor@example.org."),
    ]

    for action in actions:
        obs, rewards, costs, terminated, truncated, step_info = engine.step(action)
        print(f"  Step {step_info['step']-1}: {action.action_type} {action.name or ''}")
        if terminated or truncated:
            break

    session = engine.get_session()
    final_state = session.state
    shared = final_state.public["files"]["file_1"]["shared_with"]
    print(f"\nshared_with: {shared}")

    # Evaluate
    evaluator = hub.evaluators.get("core:share-evaluator@1.0.0")
    result = evaluator.evaluate(initial_state, final_state, engine.get_trajectory(), scenario)
    status = "PASS" if result.passed else "FAIL"
    print(f"Evaluation: {status}  score={result.score}")

    # Persist
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    store = FileStore("data")
    traj_store = TrajectoryStore(store, run_id)
    for step in engine.get_trajectory():
        traj_store.append_step(step.model_dump())
    store.write_json(f"raw/runs/{run_id}/final_state.json", final_state.model_dump())
    store.write_json(
        f"raw/runs/{run_id}/run_manifest.json",
        {
            "run_id": run_id,
            "scenario_id": scenario.scenario_id.canonical(),
            "seed": 42,
            "status": "completed",
            "passed": result.passed,
        },
    )
    print(f"Artifacts : data/raw/runs/{run_id}/")

    # Replay
    report = replay_trajectory(scenario, 42, engine.get_trajectory(), hub)
    replay_status = "PASS" if report.success else f"FAIL at step {report.first_divergent_step}"
    print(f"Replay    : {replay_status}\n")

    if not result.passed:
        print("ERROR: Evaluator did not pass.")
        return 1
    if not report.success:
        print("ERROR: Replay diverged.")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
