"""Agent adapter registry."""

from __future__ import annotations

from blindspot.agents.base import AgentAdapter
from blindspot.agents.scripted import MockAgentAdapter, ScriptedAgentAdapter


class AgentAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, AgentAdapter] = {}

    def register(self, adapter: AgentAdapter) -> None:
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str) -> AgentAdapter:
        adapter = self._adapters.get(adapter_id)
        if adapter is None:
            raise KeyError(f"No adapter registered for {adapter_id!r}")
        return adapter

    def list(self) -> list[str]:
        return list(self._adapters.keys())


def get_default_agent_registry() -> AgentAdapterRegistry:
    reg = AgentAdapterRegistry()
    reg.register(ScriptedAgentAdapter())
    reg.register(MockAgentAdapter())
    # Register Claude adapter via Bedrock (uses AWS credentials)
    try:
        from blindspot.agents.claude_adapter import ClaudeAdapter
        reg.register(ClaudeAdapter())
    except (ImportError, RuntimeError, Exception):
        pass  # No AWS credentials or SDK — skip
    return reg
