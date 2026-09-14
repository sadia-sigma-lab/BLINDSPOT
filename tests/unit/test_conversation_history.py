"""Unit tests for ConversationHistory — the critical tool round-trip fix."""

import pytest
from blindspot.agents.conversation import ConversationHistory


def test_tool_use_block_added():
    h = ConversationHistory()
    h.add_user_text("Hello")
    h.add_assistant_response([
        {"type": "text", "text": "I'll list the files."},
        {"type": "tool_use", "id": "call_123", "name": "list-files", "input": {}},
    ])
    msgs = h.to_api_messages()
    assert len(msgs) == 2
    asst = msgs[1]
    assert asst["role"] == "assistant"
    tool_use = next(b for b in asst["content"] if b.get("type") == "tool_use")
    assert tool_use["id"] == "call_123"
    assert tool_use["name"] == "list-files"


def test_tool_result_block_format():
    h = ConversationHistory()
    h.add_user_text("List files")
    h.add_assistant_response([
        {"type": "tool_use", "id": "call_abc", "name": "list-files", "input": {}},
    ])
    h.add_tool_result("call_abc", {"files": ["report.txt"]})
    msgs = h.to_api_messages()
    # Should have: user, assistant (tool_use), user (tool_result)
    assert len(msgs) == 3
    tool_result_msg = msgs[2]
    assert tool_result_msg["role"] == "user"
    content = tool_result_msg["content"]
    assert isinstance(content, list)
    assert content[0]["type"] == "tool_result"
    assert content[0]["tool_use_id"] == "call_abc"
    assert "report.txt" in content[0]["content"]


def test_tool_id_threaded_correctly():
    h = ConversationHistory()
    h.add_user_text("Do two things")
    h.add_assistant_response([
        {"type": "tool_use", "id": "id_1", "name": "list-files", "input": {}},
        {"type": "tool_use", "id": "id_2", "name": "read-file", "input": {"file_id": "f1"}},
    ])
    h.add_tool_result("id_1", {"files": []})
    h.add_tool_result("id_2", {"content": "report text"})
    msgs = h.to_api_messages()
    tool_result_msg = msgs[-1]
    assert len(tool_result_msg["content"]) == 2
    ids = {b["tool_use_id"] for b in tool_result_msg["content"]}
    assert ids == {"id_1", "id_2"}


def test_plain_text_messages():
    h = ConversationHistory()
    h.add_user_text("Hello")
    h.add_assistant_text("Hi there!")
    msgs = h.to_api_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == "Hi there!"


def test_turn_count():
    h = ConversationHistory()
    h.add_user_text("Turn 1")
    h.add_assistant_text("Reply 1")
    h.add_user_text("Turn 2")
    h.add_assistant_text("Reply 2")
    assert h.turn_count() == 2


def test_last_assistant_text():
    h = ConversationHistory()
    h.add_user_text("Hello")
    h.add_assistant_response([
        {"type": "text", "text": "I will help you."},
        {"type": "tool_use", "id": "t1", "name": "list-files", "input": {}},
    ])
    h.add_tool_result("t1", {"files": []})
    h.add_assistant_response([{"type": "text", "text": "Here are the results."}])
    assert "Here are the results." in h.last_assistant_text()


def test_empty_tool_results_handled():
    h = ConversationHistory()
    h.add_user_text("List files")
    h.add_assistant_response([
        {"type": "tool_use", "id": "t1", "name": "list-files", "input": {}},
    ])
    h.add_tool_result("t1", None)  # null result
    msgs = h.to_api_messages()
    result_msg = next(m for m in msgs if m["role"] == "user" and isinstance(m["content"], list))
    assert "(no output)" in result_msg["content"][0]["content"]


def test_readable_transcript():
    h = ConversationHistory()
    h.add_user_text("Share the report with auditor@example.org")
    h.add_assistant_response([
        {"type": "text", "text": "I'll start by listing files."},
        {"type": "tool_use", "id": "t1", "name": "list-files", "input": {}},
    ])
    h.add_tool_result("t1", {"files": ["report.txt"]})
    h.add_assistant_response([{"type": "text", "text": "Found report.txt."}])
    transcript = h.to_readable_transcript()
    assert "USER" in transcript
    assert "ASSISTANT" in transcript
    assert "list-files" in transcript


def test_messages_not_mutated_by_to_api_messages():
    h = ConversationHistory()
    h.add_user_text("Hello")
    h.add_assistant_text("Hi")
    msgs1 = h.to_api_messages()
    msgs2 = h.to_api_messages()
    assert msgs1 == msgs2
