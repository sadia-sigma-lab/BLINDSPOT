"""Agent adapter layer."""

from blindspot.agents.base import AgentAdapter
from blindspot.agents.config import AgentConfig
from blindspot.agents.response import AgentRequest, AgentResponse
from blindspot.agents.scripted import ScriptedAgentAdapter, MockAgentAdapter
from blindspot.agents.registry import AgentAdapterRegistry, get_default_agent_registry

__all__ = [
    "AgentAdapter", "AgentConfig", "AgentRequest", "AgentResponse",
    "ScriptedAgentAdapter", "MockAgentAdapter",
    "AgentAdapterRegistry", "get_default_agent_registry",
]
