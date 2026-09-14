"""Provider retry policy."""

from __future__ import annotations

from blindspot.agents.base import AgentAdapter
from blindspot.agents.config import AgentConfig
from blindspot.agents.response import AgentRequest, AgentResponse


class RetryingAdapter(AgentAdapter):
    """Wraps an adapter with configurable retry logic."""

    adapter_id = "retrying"

    def __init__(self, inner: AgentAdapter) -> None:
        self._inner = inner

    def generate(self, request: AgentRequest, config: AgentConfig) -> AgentResponse:
        last_response: AgentResponse | None = None
        for attempt in range(max(1, config.max_retries)):
            response = self._inner.generate(request, config)
            if response.error is None:
                return response
            last_response = response
        return last_response or AgentResponse(
            response_id="retry-failed", raw_content=None,
            error={"code": "MAX_RETRIES_EXCEEDED"},
        )
