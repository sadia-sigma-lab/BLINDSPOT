"""OpenAI API adapter — same interface as BedrockLLMClient.

Supports: gpt-3.5-turbo, gpt-4.5, gpt-4o, gpt-4o-mini, gpt-4-turbo, o1, o3.
Uses function-calling for tool use.

Set OPENAI_API_KEY in environment before use.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any


OPENAI_MODEL_MAP = {
    "gpt-3.5-turbo":  "gpt-3.5-turbo",
    "gpt-4.5":        "gpt-4.5-preview",
    "gpt-4o":         "gpt-4o",
    "gpt-4o-mini":    "gpt-4o-mini",
    "gpt-4-turbo":    "gpt-4-turbo",
    "o1":             "o1",
    "o3":             "o3",
    "o4-mini":        "o4-mini",
}

# Models that do not support temperature
_NO_TEMP_MODELS = ("o1", "o3", "o4-mini")


def resolve_openai_model(model: str) -> str:
    return OPENAI_MODEL_MAP.get(model, model)


class OpenAILLMClient:
    """OpenAI chat-completions wrapper with the same .complete() interface as BedrockLLMClient."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        api_key: str | None = None,
    ) -> None:
        self.model_id = resolve_openai_model(model)
        self.temperature = temperature
        self.max_tokens = max_tokens

        import openai
        self._client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Returns the same dict shape as BedrockLLMClient.complete()."""
        oai_messages = []
        if system:
            oai_messages.append({"role": "system", "content": system})

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                if isinstance(content, list):
                    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    tool_results = [c for c in content if c.get("type") == "tool_result"]
                    if tool_results:
                        for tr in tool_results:
                            oai_messages.append({
                                "role": "tool",
                                "tool_call_id": tr.get("tool_use_id", ""),
                                "content": json.dumps(tr.get("content", "")),
                            })
                        if text_parts:
                            oai_messages.append({"role": "user", "content": " ".join(text_parts)})
                    else:
                        oai_messages.append({"role": "user", "content": " ".join(text_parts)})
                else:
                    oai_messages.append({"role": "user", "content": str(content)})

            elif role == "assistant":
                if isinstance(content, list):
                    text_parts = []
                    tool_use_blocks = []
                    for c in content:
                        if c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                        elif c.get("type") == "tool_use":
                            tool_use_blocks.append({
                                "id": c.get("id", ""),
                                "type": "function",
                                "function": {
                                    "name": c.get("name", ""),
                                    "arguments": json.dumps(c.get("input", {})),
                                },
                            })
                    asst_msg: dict = {"role": "assistant"}
                    if text_parts:
                        asst_msg["content"] = " ".join(text_parts)
                    if tool_use_blocks:
                        asst_msg["tool_calls"] = tool_use_blocks
                    oai_messages.append(asst_msg)
                else:
                    oai_messages.append({"role": "assistant", "content": str(content)})

        # Build tools list (OpenAI function-calling format)
        oai_tools = None
        if tools:
            oai_tools = [self._to_openai_tool(t) for t in tools]

        try:
            params: dict[str, Any] = {
                "model": self.model_id,
                "messages": oai_messages,
                "max_tokens": self.max_tokens,
            }
            if oai_tools:
                params["tools"] = oai_tools
                params["tool_choice"] = "auto"
            if not any(m in self.model_id for m in _NO_TEMP_MODELS):
                params["temperature"] = self.temperature

            response = self._client.chat.completions.create(**params)
            choice = response.choices[0]
            msg = choice.message

            content_blocks = []
            text_parts = []
            tool_calls = []

            if msg.content:
                content_blocks.append({"type": "text", "text": msg.content})
                text_parts.append(msg.content)

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        inp = json.loads(tc.function.arguments)
                    except Exception:
                        inp = {"raw": tc.function.arguments}
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.function.name,
                        "input": inp,
                    })
                    tool_calls.append({"id": tc.id, "name": tc.function.name, "input": inp})

            stop_reason = "end_turn"
            if choice.finish_reason == "tool_calls":
                stop_reason = "tool_use"
            elif choice.finish_reason == "length":
                stop_reason = "max_tokens"

            return {
                "content_blocks": content_blocks,
                "stop_reason": stop_reason,
                "text": " ".join(text_parts),
                "tool_calls": tool_calls,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                },
                "error": None,
            }

        except Exception as exc:
            return {
                "content_blocks": [],
                "stop_reason": "error",
                "text": "",
                "tool_calls": [],
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }

    @staticmethod
    def _to_openai_tool(t: dict) -> dict:
        return {
            "type": "function",
            "function": {
                "name": t.get("name", ""),
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", t.get("parameters", {"type": "object", "properties": {}})),
            },
        }
