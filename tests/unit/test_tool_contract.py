"""Unit tests for tool contracts."""

import pytest

from blindspot.core.state import WorldState
from blindspot.core.tool import ExecutionContext


def _state() -> WorldState:
    return WorldState(
        schema_version="1.0",
        episode_id="ep1",
        step=0,
        session_id="sess1",
        random_seed=42,
        public={
            "files": {
                "file_1": {
                    "name": "report.txt",
                    "owner_id": "user_1",
                    "content": "Quarterly report",
                    "shared_with": [],
                }
            }
        },
        private={},
        hidden={"secret": "do-not-leak"},
        audit_log=[],
    )


def _ctx() -> ExecutionContext:
    return ExecutionContext(session_id="sess1", actor_id="agent", step=0)


def test_read_only_tool_returns_empty_diff() -> None:
    from examples.minimal_domain.tools import ListFilesTool

    tool = ListFilesTool()
    result = tool.execute(_state(), "agent", {}, _ctx())
    assert result.success
    assert result.state_diff.is_empty


def test_mutating_tool_returns_valid_diff() -> None:
    from examples.minimal_domain.tools import ShareFileTool

    tool = ShareFileTool()
    result = tool.execute(
        _state(), "agent", {"file_id": "file_1", "recipient": "x@example.org"}, _ctx()
    )
    assert result.success
    assert not result.state_diff.is_empty
    assert result.state_diff.mutations[0].operation == "replace"


def test_invalid_arguments_fail_cleanly() -> None:
    from examples.minimal_domain.tools import ReadFileTool

    tool = ReadFileTool()
    result = tool.execute(_state(), "agent", {}, _ctx())
    assert not result.success
    assert result.error_code == "MISSING_ARG"


def test_tool_cannot_expose_hidden_state() -> None:
    from examples.minimal_domain.tools import ListFilesTool

    tool = ListFilesTool()
    result = tool.execute(_state(), "agent", {}, _ctx())
    output_str = str(result.output)
    assert "do-not-leak" not in output_str


def test_audit_entry_produced() -> None:
    from examples.minimal_domain.tools import ListFilesTool

    tool = ListFilesTool()
    result = tool.execute(_state(), "agent", {}, _ctx())
    assert len(result.audit_entries) > 0
    assert result.audit_entries[0]["action"] == "list_files"
