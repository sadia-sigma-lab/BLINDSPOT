"""Multi-strategy action parser with priority fallback."""

from __future__ import annotations

import json
import uuid
from typing import Any

from blindspot.agents.response import AgentResponse
from blindspot.core.action import AgentAction
from blindspot.parsing.base import ParseResult


def parse_native_tool_calls(response: AgentResponse, enabled_tools: set[str]) -> ParseResult:
    """Parse native provider tool-call entries from the response."""
    if not response.native_tool_calls:
        return ParseResult(success=False, parser_id="native_tool")

    tc = response.native_tool_calls[0]
    tool_name = tc.get("function", {}).get("name") or tc.get("name", "")
    args_raw = tc.get("function", {}).get("arguments") or tc.get("arguments", {})

    if not tool_name:
        return ParseResult(
            success=False, parser_id="native_tool",
            errors=[{"code": "MISSING_TOOL_NAME"}],
        )
    if tool_name not in enabled_tools:
        return ParseResult(
            success=False, parser_id="native_tool",
            errors=[{"code": "UNKNOWN_TOOL", "tool": tool_name}],
        )

    if isinstance(args_raw, str):
        try:
            args = json.loads(args_raw)
        except json.JSONDecodeError:
            args = {}
    else:
        args = args_raw or {}

    return ParseResult(
        success=True,
        action=AgentAction(
            action_id=str(uuid.uuid4()),
            action_type="tool_call",
            name=tool_name,
            arguments=args,
        ),
        parser_id="native_tool",
    )


def parse_json_action(text: str, enabled_tools: set[str]) -> ParseResult:
    """Parse a JSON-encoded action from response text."""
    try:
        data = json.loads(text.strip())
        if not isinstance(data, dict):
            raise ValueError("Expected a dict")
    except Exception:
        return ParseResult(success=False, parser_id="json_action",
                           errors=[{"code": "NOT_JSON"}])

    action_type = data.get("action_type", data.get("type", "message"))
    tool_name = data.get("name") or data.get("tool")
    arguments = data.get("arguments", data.get("args", {}))
    content = data.get("content")

    if action_type == "tool_call" and tool_name:
        if tool_name not in enabled_tools:
            return ParseResult(success=False, parser_id="json_action",
                               errors=[{"code": "UNKNOWN_TOOL", "tool": tool_name}])
        return ParseResult(
            success=True,
            action=AgentAction(action_id=str(uuid.uuid4()), action_type="tool_call",
                               name=tool_name, arguments=arguments or {}),
            parser_id="json_action",
        )

    if action_type in ("refuse", "escalate", "no_op", "rollback", "ask_user", "request_approval"):
        return ParseResult(
            success=True,
            action=AgentAction(action_id=str(uuid.uuid4()), action_type=action_type,
                               content=content),
            parser_id="json_action",
        )

    return ParseResult(
        success=True,
        action=AgentAction(action_id=str(uuid.uuid4()), action_type="message", content=content or text),
        parser_id="json_action",
    )


def parse_message_fallback(response: AgentResponse) -> ParseResult:
    """Final fallback — treat any text response as a message action."""
    text = response.text or str(response.raw_content or "")

    # Detect refusal patterns
    lower = text.lower()
    if any(phrase in lower for phrase in ["i cannot", "i can't", "i refuse", "i won't", "not allowed"]):
        return ParseResult(
            success=True,
            action=AgentAction(action_id=str(uuid.uuid4()), action_type="refuse", content=text),
            parser_id="message_fallback",
        )

    return ParseResult(
        success=True,
        action=AgentAction(action_id=str(uuid.uuid4()), action_type="message", content=text),
        parser_id="message_fallback",
    )


def parse_response(
    response: AgentResponse,
    enabled_tools: set[str],
) -> ParseResult:
    """Main dispatcher — priority: native tool → JSON → message fallback."""
    # 1. Native tool calls
    if response.native_tool_calls:
        result = parse_native_tool_calls(response, enabled_tools)
        if result.success:
            return result

    # 2. JSON action from text
    text = response.text or ""
    if text.strip().startswith("{"):
        result = parse_json_action(text, enabled_tools)
        if result.success:
            return result

    # 3. Message fallback
    return parse_message_fallback(response)
