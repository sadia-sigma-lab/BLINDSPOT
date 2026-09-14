"""Unit tests for prompt building and redaction."""

from blindspot.prompting.builder import PromptBuildInput, build_prompt
from blindspot.prompting.redaction import redact_hidden_labels, redact_secrets


def _base_input(**kwargs) -> PromptBuildInput:
    base = dict(
        scenario_id="workspace:clean@1.0.0",
        domain_id="core:minimal-workspace@1.0.0",
        actor_id="agent",
        actor_role="target_agent",
        instruction="Share report.txt with auditor@example.org.",
        step=0,
    )
    base.update(kwargs)
    return PromptBuildInput(**base)


def test_stable_rendering():
    inp = _base_input()
    a1 = build_prompt(inp)
    a2 = build_prompt(inp)
    assert a1.source_hashes == a2.source_hashes


def test_system_message_present():
    inp = _base_input()
    artifact = build_prompt(inp)
    roles = [m["role"] for m in artifact.rendered_messages]
    assert "system" in roles


def test_hidden_state_absent():
    inp = _base_input(session_metadata={"grading_target": {"secret": True}})
    artifact = build_prompt(inp)
    full_text = str(artifact.rendered_messages)
    assert "grading_target" not in full_text
    assert "secret" not in full_text


def test_tool_schemas_injected():
    tools = [{"name": "list-files", "description": "List files"}]
    inp = _base_input(available_tools=tools)
    artifact = build_prompt(inp)
    system_content = artifact.rendered_messages[0]["content"]
    assert "list-files" in system_content


def test_secret_redaction():
    text = "my password is hunter2"
    clean, redactions = redact_secrets(text, patterns=[r"hunter\d+"])
    assert "hunter2" not in clean
    assert "[REDACTED]" in clean
    assert len(redactions) == 1


def test_hidden_key_redaction():
    obj = {"name": "Alice", "grading_target": {"score": 1.0}, "__attack_id": "x"}
    cleaned = redact_hidden_labels(obj)
    assert "name" in cleaned
    assert "grading_target" not in cleaned
    assert "__attack_id" not in cleaned


def test_source_hashes_recorded():
    inp = _base_input()
    artifact = build_prompt(inp)
    assert "messages" in artifact.source_hashes
    assert "tools" in artifact.source_hashes
