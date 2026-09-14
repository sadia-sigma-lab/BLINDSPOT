"""Prompt builder — assembles actor-specific prompts with provenance."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.prompting.provenance import compute_source_hashes
from blindspot.prompting.redaction import redact_hidden_labels
from blindspot.prompting.templates import (
    render_observation_section,
    render_policies_section,
    render_system_prompt,
    render_task_section,
    render_tools_section,
)


_TEMPLATE_IDS = [
    "system@1.0.0",
    "task@1.0.0",
    "policies@1.0.0",
    "tools@1.0.0",
    "observation@1.0.0",
]


class PromptBuildInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: str
    domain_id: str
    actor_id: str
    actor_role: str
    instruction: str
    step: int
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    visible_policies: list[str] = Field(default_factory=list)
    available_tools: list[dict[str, Any]] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    retrieved_memory: list[dict[str, Any]] = Field(default_factory=list)
    session_metadata: dict[str, Any] = Field(default_factory=dict)
    redaction_patterns: list[str] = Field(default_factory=list)


class PromptArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    prompt_id: str
    rendered_messages: list[dict[str, Any]]
    template_ids: list[str]
    source_hashes: dict[str, str]
    redactions: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_prompt(inp: PromptBuildInput, secret_patterns: list[str] | None = None) -> PromptArtifact:
    """Build a complete, ordered prompt with provenance."""
    messages: list[dict[str, Any]] = []

    # 1. System instructions + actor role
    system_text = render_system_prompt(inp.actor_role, inp.domain_id)

    # 2. Benign task objective
    task_text = render_task_section(inp.instruction)

    # 3. Visible policies
    policies_text = render_policies_section(inp.visible_policies)

    # 4. Discoverable tools
    clean_tools = [redact_hidden_labels(t) for t in inp.available_tools]
    tools_text = render_tools_section(clean_tools)

    # Compose system message
    system_content = system_text + task_text + policies_text + tools_text
    messages.append({"role": "system", "content": system_content})

    # 5. Conversation history (clean — already projected)
    for hist_msg in inp.conversation_history:
        clean_msg = redact_hidden_labels(dict(hist_msg))
        messages.append(clean_msg)

    # 6. Retrieved memory (no hidden labels)
    for mem in inp.retrieved_memory:
        clean_mem = redact_hidden_labels(dict(mem))
        messages.append({"role": "system", "content": f"[memory]: {clean_mem.get('content', '')}"})

    # 7. Current observation
    obs_text = render_observation_section(inp.step, inp.messages, inp.tool_results)
    messages.append({"role": "user", "content": obs_text})

    # Redact secrets from all message content
    all_redactions: list[dict[str, Any]] = []
    if secret_patterns:
        from blindspot.prompting.redaction import redact_secrets
        cleaned: list[dict[str, Any]] = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                clean_content, redaction_log = redact_secrets(content, secret_patterns)
                cleaned.append({**msg, "content": clean_content})
                all_redactions.extend(redaction_log)
            else:
                cleaned.append(msg)
        messages = cleaned

    source_hashes = compute_source_hashes(messages, clean_tools, _TEMPLATE_IDS)

    return PromptArtifact(
        prompt_id=str(uuid.uuid4()),
        rendered_messages=messages,
        template_ids=list(_TEMPLATE_IDS),
        source_hashes=source_hashes,
        redactions=all_redactions,
        metadata={"actor_id": inp.actor_id, "step": inp.step},
    )
