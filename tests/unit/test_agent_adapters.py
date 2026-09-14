"""Unit tests for agent adapters and simulators."""

import uuid
from blindspot.agents.config import AgentConfig
from blindspot.agents.scripted import ScriptedAgentAdapter, MockAgentAdapter
from blindspot.agents.response import AgentRequest
from blindspot.agents.retry import RetryingAdapter
from blindspot.simulators.scripted import UserSimulator, ApproverSimulator, MonitorSimulator


def _config():
    return AgentConfig(agent_id="t", adapter_id="scripted", model_name="t", provider="local")


def _request():
    return AgentRequest(run_id="r", episode_id="e", session_id="s", step=0, messages=[], tools=[])


def test_scripted_returns_script_entries():
    adapter = ScriptedAgentAdapter([
        {"text": "hello", "tool_calls": [], "finish_reason": "stop"},
    ])
    resp = adapter.generate(_request(), _config())
    assert resp.text == "hello"


def test_scripted_loops_on_last():
    adapter = ScriptedAgentAdapter([{"text": "last", "tool_calls": [], "finish_reason": "stop"}])
    for _ in range(5):
        resp = adapter.generate(_request(), _config())
        assert resp.text == "last"


def test_mock_returns_fixed():
    adapter = MockAgentAdapter({"text": "done", "finish_reason": "stop"})
    resp = adapter.generate(_request(), _config())
    assert resp.text == "done"


def test_usage_recorded():
    adapter = MockAgentAdapter({"text": "x"})
    resp = adapter.generate(_request(), _config())
    assert resp.usage is not None


def test_retrying_adapter_returns_on_success():
    inner = MockAgentAdapter({"text": "ok"})
    adapter = RetryingAdapter(inner)
    resp = adapter.generate(_request(), _config())
    assert resp.error is None


def test_user_simulator_sends_instruction():
    sim = UserSimulator(["Share report.txt"])
    from blindspot.core.observation import Observation
    obs = Observation(step=0, session_id="s", messages=[], tool_results=[],
                      notifications=[], available_tools=[])
    from blindspot.simulation.context import SimulationContext
    from datetime import datetime, timezone
    ctx = SimulationContext(run_id="r", episode_id="e", scenario_id="s",
                             domain_id="d", session_id="ss", seed=42,
                             current_time=datetime(2026, 6, 1, tzinfo=timezone.utc))
    sim.initialize(None, None, 42)
    action = sim.act(obs, ctx)
    assert action.action_type == "message"
    assert "Share" in (action.content or "")


def test_monitor_is_no_op():
    from blindspot.core.observation import Observation
    from blindspot.simulation.context import SimulationContext
    from datetime import datetime, timezone
    obs = Observation(step=0, session_id="s", messages=[], tool_results=[],
                      notifications=[], available_tools=[])
    ctx = SimulationContext(run_id="r", episode_id="e", scenario_id="s",
                             domain_id="d", session_id="ss", seed=42,
                             current_time=datetime(2026, 6, 1, tzinfo=timezone.utc))
    sim = MonitorSimulator()
    sim.initialize(None, None, 42)
    action = sim.act(obs, ctx)
    assert action.action_type == "no_op"
