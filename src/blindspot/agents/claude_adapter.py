"""Claude adapter using AWS Bedrock (AnthropicBedrock client).

Uses the same `anthropic` SDK with the BedrockBackend — no separate API key needed,
credentials come from the AWS environment (IAM role / instance profile / env vars).
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from blindspot.agents.base import AgentAdapter
from blindspot.agents.config import AgentConfig
from blindspot.agents.response import AgentRequest, AgentResponse

# Default: cross-region inference profile for Claude Opus 4.6
BEDROCK_DEFAULT_MODEL = "us.anthropic.claude-opus-4-6-v1"
BEDROCK_DEFAULT_REGION = "us-east-1"

# Map short model names → Bedrock inference profile IDs
_MODEL_ID_MAP = {
    # Claude Opus 4.6
    "claude-opus-4-6":        "us.anthropic.claude-opus-4-6-v1",
    "anthropic.claude-opus-4-6-v1": "us.anthropic.claude-opus-4-6-v1",
    "us.anthropic.claude-opus-4-6-v1": "us.anthropic.claude-opus-4-6-v1",
    # Claude Opus 5
    "claude-opus-5":          "us.anthropic.claude-opus-5",
    "anthropic.claude-opus-5": "us.anthropic.claude-opus-5",
    # Claude Sonnet 4.6
    "claude-sonnet-4-6":      "us.anthropic.claude-sonnet-4-6",
    # Claude Haiku 4.5
    "claude-haiku-4-5":       "anthropic.claude-haiku-4-5-20251001-v1:0",
}


def _resolve_bedrock_model(model_name: str) -> str:
    """Convert a short model name to the correct Bedrock inference profile ID."""
    return _MODEL_ID_MAP.get(model_name, model_name)


def _build_tool_schema(tool: dict[str, Any]) -> dict[str, Any]:
    """Convert benchmark tool schema to Anthropic tool format."""
    if "function" in tool:
        fn = tool["function"]
        name = fn.get("name", "unknown")
        description = fn.get("description", "")
        parameters = fn.get("parameters", {"type": "object", "properties": {}})
    else:
        name = tool.get("name", "unknown")
        description = tool.get("description", "")
        parameters = tool.get("parameters", tool.get("input_schema", {
            "type": "object", "properties": {}
        }))
    return {
        "name": name,
        "description": description,
        "input_schema": parameters or {"type": "object", "properties": {}},
    }


class ClaudeAdapter(AgentAdapter):
    """Claude adapter via AWS Bedrock — uses existing AWS credentials."""

    adapter_id = "claude"

    def __init__(self, aws_region: str = BEDROCK_DEFAULT_REGION) -> None:
        try:
            from anthropic import AnthropicBedrock
            self._AnthropicBedrock = AnthropicBedrock
        except ImportError:
            raise ImportError(
                "anthropic SDK with Bedrock support required.\n"
                "Run: pip install anthropic"
            )
        self._region = aws_region
        # Validate AWS credentials are available
        try:
            self._client = AnthropicBedrock(aws_region=aws_region)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize Bedrock client: {exc}\n"
                "Ensure AWS credentials are configured (IAM role, env vars, or ~/.aws/credentials)"
            ) from exc

    def generate(self, request: AgentRequest, config: AgentConfig) -> AgentResponse:
        t_start = time.monotonic()

        # ── 1. Resolve Bedrock model ID ───────────────────────────────────────
        bedrock_model = _resolve_bedrock_model(config.model_name)

        # ── 2. Build messages ─────────────────────────────────────────────────
        system_parts: list[str] = []
        api_messages: list[dict] = []

        for msg in request.messages:
            role = msg.get("role", "user")
            content = str(msg.get("content") or "").strip()
            if not content:
                continue
            if role == "system":
                system_parts.append(content)
            elif role in ("user", "assistant"):
                api_messages.append({"role": role, "content": content})
            elif role == "tool_result":
                api_messages.append({"role": "user",
                                      "content": f"[Tool result]: {content}"})

        if not api_messages:
            api_messages = [{"role": "user",
                              "content": "Please begin working on the task."}]

        system_text = "\n\n".join(system_parts) if system_parts else (
            "You are a helpful AI assistant in a workspace environment. "
            "Complete the task step by step using the available tools. "
            "Call tools to gather information and make changes. "
            "Only send a plain text message when you have fully completed the task."
        )

        # ── 3. Convert tool schemas ───────────────────────────────────────────
        anthropic_tools = []
        for tool in (request.tools or []):
            try:
                anthropic_tools.append(_build_tool_schema(tool))
            except Exception:
                pass

        # ── 4. API call ───────────────────────────────────────────────────────
        params: dict[str, Any] = {
            "model": bedrock_model,
            "max_tokens": config.max_output_tokens or 2048,
            "system": system_text,
            "messages": api_messages,
        }
        if anthropic_tools:
            params["tools"] = anthropic_tools
        if config.temperature and config.temperature != 0.0:
            params["temperature"] = config.temperature

        try:
            response = self._client.messages.create(**params)
            latency_ms = (time.monotonic() - t_start) * 1000

            # ── 5. Parse response ─────────────────────────────────────────────
            text_parts: list[str] = []
            native_tool_calls: list[dict] = []

            for block in response.content:
                btype = getattr(block, "type", "")
                if btype == "text":
                    txt = getattr(block, "text", "")
                    if txt:
                        text_parts.append(txt)
                elif btype == "tool_use":
                    tool_input = getattr(block, "input", {})
                    if isinstance(tool_input, str):
                        try:
                            tool_input = json.loads(tool_input)
                        except Exception:
                            tool_input = {}
                    native_tool_calls.append({
                        "id": getattr(block, "id", str(uuid.uuid4())),
                        "function": {
                            "name": getattr(block, "name", ""),
                            "arguments": json.dumps(tool_input),
                        },
                        "name": getattr(block, "name", ""),
                        "arguments": tool_input,
                    })

            full_text = "\n".join(text_parts).strip()
            finish_reason = getattr(response, "stop_reason", "end_turn")

            usage: dict[str, Any] = {}
            if hasattr(response, "usage"):
                u = response.usage
                usage = {
                    "input_tokens": getattr(u, "input_tokens", 0),
                    "output_tokens": getattr(u, "output_tokens", 0),
                }

            return AgentResponse(
                response_id=str(uuid.uuid4()),
                raw_content={"text": full_text, "tool_calls": native_tool_calls},
                text=full_text if full_text else None,
                native_tool_calls=native_tool_calls,
                finish_reason=finish_reason,
                usage=usage,
                latency_ms=latency_ms,
                provider_metadata={
                    "model": bedrock_model,
                    "stop_reason": finish_reason,
                    "provider": "bedrock",
                },
            )

        except Exception as exc:
            latency_ms = (time.monotonic() - t_start) * 1000
            err_name = type(exc).__name__
            err_msg = str(exc)

            # Raise immediately on credential / permission errors
            if "credentials" in err_msg.lower() or "auth" in err_msg.lower() or \
               "AccessDenied" in err_msg or "UnrecognizedClientException" in err_msg:
                raise RuntimeError(
                    f"AWS Bedrock authentication failed: {err_msg}"
                ) from exc

            return AgentResponse(
                response_id=str(uuid.uuid4()),
                raw_content=None,
                text=None,
                error={"code": err_name, "message": err_msg},
                latency_ms=latency_ms,
            )
