"""Versioned prompt template loading and rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any


_TEMPLATE_VERSION = "1.0.0"

# Built-in inline templates (no file dependency for tests)
_SYSTEM_TEMPLATE = """You are a helpful AI assistant operating within a workspace.
Version: {template_version}

Your role: {actor_role}
Domain: {domain_id}
"""

_TASK_TEMPLATE = """## Your current task

{instruction}
"""

_POLICIES_TEMPLATE = """## Applicable policies

{policies}
"""

_TOOLS_TEMPLATE = """## Available tools

You have access to the following tools:
{tool_list}
"""

_OBSERVATION_TEMPLATE = """## Current observation

Step: {step}
{observation_text}
"""


def render_system_prompt(
    actor_role: str,
    domain_id: str,
    template_version: str = _TEMPLATE_VERSION,
) -> str:
    return _SYSTEM_TEMPLATE.format(
        template_version=template_version,
        actor_role=actor_role,
        domain_id=domain_id,
    )


def render_task_section(instruction: str) -> str:
    return _TASK_TEMPLATE.format(instruction=instruction)


def render_policies_section(policies: list[str]) -> str:
    if not policies:
        return ""
    return _POLICIES_TEMPLATE.format(policies="\n".join(f"- {p}" for p in policies))


def render_tools_section(tools: list[dict[str, Any]]) -> str:
    if not tools:
        return "No tools available."
    lines = [f"- {t.get('name', t.get('function', {}).get('name', 'unknown'))}: {t.get('description', '')}" for t in tools]
    return _TOOLS_TEMPLATE.format(tool_list="\n".join(lines))


def render_observation_section(step: int, messages: list[dict[str, Any]], tool_results: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        parts.append(f"[{role}]: {content}")
    for tr in tool_results:
        parts.append(f"[tool_result]: {tr}")
    obs_text = "\n".join(parts) if parts else "(no new messages)"
    return _OBSERVATION_TEMPLATE.format(step=step, observation_text=obs_text)
