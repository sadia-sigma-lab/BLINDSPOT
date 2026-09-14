"""Deterministic scripted agent adapter."""

from __future__ import annotations

import uuid
from typing import Any

from blindspot.agents.base import AgentAdapter
from blindspot.agents.config import AgentConfig
from blindspot.agents.response import AgentRequest, AgentResponse


class ScriptedAgentAdapter(AgentAdapter):
    """Returns pre-defined responses from a script list."""

    adapter_id = "scripted"

    def __init__(self, script: list[dict[str, Any]] | None = None) -> None:
        self._script = script or []
        self._index = 0

    def set_script(self, script: list[dict[str, Any]]) -> None:
        self._script = script
        self._index = 0

    def generate(self, request: AgentRequest, config: AgentConfig) -> AgentResponse:
        if not self._script:
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                raw_content=None,
                text="No script configured.",
                finish_reason="stop",
            )
        idx = min(self._index, len(self._script) - 1)
        entry = self._script[idx]
        self._index += 1
        tool_calls = entry.get("tool_calls", [])
        # Normalize tool call format: {name, arguments} → {function: {name, arguments}}
        normalized_tcs = []
        for tc in tool_calls:
            if "function" not in tc:
                normalized_tcs.append({"function": {"name": tc.get("name", ""), "arguments": tc.get("arguments", {})}})
            else:
                normalized_tcs.append(tc)
        return AgentResponse(
            response_id=str(uuid.uuid4()),
            raw_content=entry,
            text=entry.get("text"),
            native_tool_calls=normalized_tcs,
            finish_reason=entry.get("finish_reason", "stop"),
            usage={"input_tokens": 0, "output_tokens": 0},
        )


class MockAgentAdapter(AgentAdapter):
    """Returns a configurable fixed response — for testing."""

    adapter_id = "mock"

    def __init__(self, fixed_response: dict[str, Any] | None = None) -> None:
        self._response = fixed_response or {"text": "Task completed.", "finish_reason": "stop"}

    def generate(self, request: AgentRequest, config: AgentConfig) -> AgentResponse:
        return AgentResponse(
            response_id=str(uuid.uuid4()),
            raw_content=self._response,
            text=self._response.get("text"),
            native_tool_calls=self._response.get("tool_calls", []),
            finish_reason=self._response.get("finish_reason", "stop"),
            usage={"input_tokens": len(str(request.messages)), "output_tokens": 10},
        )
