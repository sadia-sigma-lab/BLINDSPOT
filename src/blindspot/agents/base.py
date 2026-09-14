"""Abstract agent adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from blindspot.agents.config import AgentConfig
from blindspot.agents.response import AgentRequest, AgentResponse


class AgentAdapter(ABC):
    """Abstract interface for calling an AI model or scripted agent."""

    adapter_id: str

    @abstractmethod
    def generate(self, request: AgentRequest, config: AgentConfig) -> AgentResponse:
        """Send a request and return a response."""
        ...
