"""Unit tests for action parsing and repair."""

import uuid
import pytest
from blindspot.agents.response import AgentResponse
from blindspot.parsing.action_parser import parse_response, parse_native_tool_calls
from blindspot.parsing.repair import RepairPolicy, attempt_repair
from blindspot.parsing.base import ParseResult


def _resp(**kwargs) -> AgentResponse:
    return AgentResponse(response_id=str(uuid.uuid4()), raw_content=None, **kwargs)


_TOOLS = {"list-files", "read-file", "share-file"}


def test_native_tool_call_parsed():
    resp = _resp(native_tool_calls=[{"function": {"name": "list-files", "arguments": {}}}])
    result = parse_response(resp, _TOOLS)
    assert result.success
    assert result.action.name == "list-files"
    assert result.action.action_type == "tool_call"


def test_unknown_tool_rejected():
    resp = _resp(native_tool_calls=[{"function": {"name": "evil-tool", "arguments": {}}}])
    result = parse_native_tool_calls(resp, _TOOLS)
    assert not result.success
    assert result.errors[0]["code"] == "UNKNOWN_TOOL"


def test_json_tool_call():
    import json
    resp = _resp(text=json.dumps({"action_type": "tool_call", "name": "read-file",
                                   "arguments": {"file_id": "f1"}}))
    result = parse_response(resp, _TOOLS)
    assert result.success
    assert result.action.name == "read-file"


def test_refusal_detected():
    resp = _resp(text="I cannot share confidential files without approval.")
    result = parse_response(resp, _TOOLS)
    assert result.success
    assert result.action.action_type == "refuse"


def test_message_fallback():
    resp = _resp(text="Here is the file content.")
    result = parse_response(resp, _TOOLS)
    assert result.success
    assert result.action.action_type == "message"


def test_deterministic_repair():
    resp = _resp(text='Thinking... call list-files()')
    failed_result = ParseResult(success=False, errors=[{"code": "INITIAL_FAIL"}], parser_id="test")
    policy = RepairPolicy(enabled=True, max_attempts=1)
    repaired = attempt_repair(resp, failed_result, policy, _TOOLS)
    assert repaired.success
    assert repaired.repair_attempted


def test_repair_exhausted():
    resp = _resp(text="garbled text no JSON here")
    failed = ParseResult(success=False, errors=[], parser_id="test")
    policy = RepairPolicy(enabled=True, max_attempts=1, strategy="deterministic")
    result = attempt_repair(resp, failed, policy, _TOOLS, attempt=1)
    assert not result.success
    assert result.repair_attempted
