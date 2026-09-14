"""Bounded parse repair — deterministic normalization only."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from blindspot.agents.response import AgentResponse
from blindspot.core.action import AgentAction
from blindspot.parsing.action_parser import parse_response
from blindspot.parsing.base import ParseResult


class RepairPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    max_attempts: int = 1
    strategy: Literal["deterministic", "self_repair", "secondary_parser", "none"] = "deterministic"


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    """Try to extract a JSON object from freeform text."""
    match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


def attempt_repair(
    response: AgentResponse,
    parse_result: ParseResult,
    policy: RepairPolicy,
    enabled_tools: set[str],
    attempt: int = 0,
) -> ParseResult:
    """Apply deterministic repair to a failed parse result."""
    if not policy.enabled or policy.strategy == "none":
        return parse_result
    if attempt >= policy.max_attempts:
        return ParseResult(
            success=False,
            errors=[{"code": "REPAIR_EXHAUSTED", "attempts": attempt}],
            repair_attempted=True,
            parser_id="deterministic_repair",
        )

    text = response.text or str(response.raw_content or "")

    # Deterministic repair: try to extract JSON from freeform text
    extracted = _extract_json_from_text(text)
    if extracted:
        mock_text = json.dumps(extracted)
        from blindspot.parsing.action_parser import parse_json_action
        repaired = parse_json_action(mock_text, enabled_tools)
        if repaired.success:
            return ParseResult(
                success=True,
                action=repaired.action,
                repair_attempted=True,
                repair_output=extracted,
                parser_id="deterministic_repair",
            )

    # Try to detect tool call in text like "call list_files()"
    tool_match = re.search(r"call\s+([a-z_-]+)\s*\((.*?)\)", text, re.IGNORECASE | re.DOTALL)
    if tool_match:
        tool_name = tool_match.group(1)
        if tool_name in enabled_tools:
            args_text = tool_match.group(2).strip()
            try:
                args = json.loads(args_text) if args_text else {}
            except Exception:
                args = {}
            return ParseResult(
                success=True,
                action=AgentAction(
                    action_id=str(uuid.uuid4()),
                    action_type="tool_call",
                    name=tool_name,
                    arguments=args,
                ),
                repair_attempted=True,
                repair_output=tool_match.group(0),
                parser_id="deterministic_repair",
            )

    # Exhausted repair — return explicit failure
    return ParseResult(
        success=False,
        errors=[{"code": "REPAIR_EXHAUSTED", "attempts": attempt + 1}],
        repair_attempted=True,
        parser_id="deterministic_repair",
    )
