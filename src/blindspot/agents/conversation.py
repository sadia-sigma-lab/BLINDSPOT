"""Typed conversation history using Anthropic's native tool-use/tool-result format.

This is the CRITICAL fix for the tool-result propagation bug.

Broken (current): tool results fed as plain text "[Tool result]: ..."
                  → Claude ignores them → infinite loop

Fixed (this):     tool results fed as proper tool_result content blocks
                  {type: tool_result, tool_use_id: ..., content: ...}
                  → Claude sees actual results → reasons and progresses
"""

from __future__ import annotations

import json
import uuid
from typing import Any


class ConversationHistory:
    """
    Manages a full conversation in Anthropic's native message format.

    Supports:
    - Plain text user/assistant turns
    - Native tool_use blocks (assistant calls a tool)
    - Native tool_result blocks (tool execution result fed back)

    The key invariant: every tool_use block must be immediately followed
    by a user message containing a tool_result block with the same id.
    """

    def __init__(self) -> None:
        self._messages: list[dict[str, Any]] = []
        self._pending_tool_uses: list[dict[str, Any]] = []

    def add_user_text(self, text: str) -> None:
        """Add a plain text user message."""
        if not text.strip():
            return
        # If there are pending tool results to collect, add as separate turn
        self._flush_pending_tool_results()
        self._messages.append({"role": "user", "content": text})

    def add_assistant_text(self, text: str) -> None:
        """Add a plain text assistant message."""
        if not text.strip():
            return
        self._flush_pending_tool_results()
        self._messages.append({"role": "assistant", "content": text})

    def add_assistant_response(self, content_blocks: list[dict[str, Any]]) -> None:
        """
        Add a full assistant response with content blocks.

        content_blocks: list of Anthropic content block dicts
          e.g. [{"type": "text", "text": "..."}, {"type": "tool_use", "id": ..., "name": ..., "input": ...}]

        Tracks pending tool_use IDs that need tool_result responses.
        """
        self._flush_pending_tool_results()

        # Filter to valid non-empty blocks
        valid_blocks = []
        pending = []
        for block in content_blocks:
            btype = block.get("type", "")
            if btype == "text":
                if block.get("text", "").strip():
                    valid_blocks.append(block)
            elif btype == "tool_use":
                valid_blocks.append(block)
                pending.append({
                    "tool_use_id": block.get("id", str(uuid.uuid4())),
                    "name": block.get("name", ""),
                })
            elif btype in ("thinking", "redacted_thinking"):
                pass  # skip
            else:
                valid_blocks.append(block)

        if valid_blocks:
            self._messages.append({"role": "assistant", "content": valid_blocks})
        elif pending:
            # Edge case: only tool_use blocks with no text
            self._messages.append({"role": "assistant", "content": [b for b in content_blocks if b.get("type") == "tool_use"]})

        self._pending_tool_uses.extend(pending)

    def add_tool_result(
        self,
        tool_use_id: str,
        content: Any,
        is_error: bool = False,
    ) -> None:
        """
        Record the result of a tool call.

        Must be called after add_assistant_response has added a tool_use block
        with the corresponding tool_use_id. The results are batched and sent
        as a single user message when _flush_pending_tool_results() is called
        (i.e., before the next assistant turn).
        """
        if is_error:
            result_content = f"Error: {content}" if not isinstance(content, str) else content
        else:
            if content is None:
                result_content = "(no output)"
            elif isinstance(content, (dict, list)):
                result_content = json.dumps(content, default=str)[:2000]  # cap length
            else:
                result_content = str(content)[:2000]

        # Store for batching — all tool results for one assistant turn go in one user msg
        if not hasattr(self, "_buffered_results"):
            self._buffered_results: list[dict] = []
        self._buffered_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result_content,
            **({"is_error": True} if is_error else {}),
        })

    def _flush_pending_tool_results(self) -> None:
        """Send all buffered tool results as a single user message."""
        buffered = getattr(self, "_buffered_results", [])
        if buffered:
            self._messages.append({"role": "user", "content": list(buffered)})
            self._buffered_results = []
            self._pending_tool_uses.clear()

    def flush(self) -> None:
        """Force-flush any buffered tool results."""
        self._flush_pending_tool_results()

    def to_api_messages(self) -> list[dict[str, Any]]:
        """Return messages in Anthropic API format, ensuring tool results are flushed."""
        self._flush_pending_tool_results()
        return list(self._messages)

    def last_assistant_text(self) -> str:
        """Return the text content of the last assistant message."""
        for msg in reversed(self._messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    parts = [b.get("text", "") for b in content if b.get("type") == "text"]
                    return "\n".join(parts).strip()
        return ""

    def turn_count(self) -> int:
        """Number of user→assistant turn pairs."""
        return sum(1 for m in self._messages if m.get("role") == "user")

    def to_readable_transcript(self) -> str:
        """Human-readable transcript for judge evaluation — full content, no truncation."""
        lines: list[str] = []
        self._flush_pending_tool_results()
        turn = 0
        for msg in self._messages:
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if role == "user":
                turn += 1
                if isinstance(content, str):
                    lines.append(f"\n[Turn {turn} USER]\n{content}")
                elif isinstance(content, list):
                    for block in content:
                        if block.get("type") == "tool_result":
                            tool_id = block.get("tool_use_id", "?")
                            result_content = block.get("content", "")
                            # Serialize dict/list content to readable JSON
                            if isinstance(result_content, (dict, list)):
                                result_str = json.dumps(result_content, default=str, indent=None)
                            else:
                                result_str = str(result_content)
                            lines.append(f"[Tool Result ({tool_id[:12]})] {result_str}")
                        elif block.get("type") == "text":
                            lines.append(f"\n[Turn {turn} USER]\n{block.get('text','')}")
            elif role == "assistant":
                if isinstance(content, str):
                    lines.append(f"\n[ASSISTANT]\n{content}")
                elif isinstance(content, list):
                    for block in content:
                        if block.get("type") == "text":
                            lines.append(f"\n[ASSISTANT]\n{block.get('text','')}")
                        elif block.get("type") == "tool_use":
                            input_str = json.dumps(block.get("input", {}), default=str)
                            lines.append(f"[Tool Call: {block.get('name','')}({input_str})]")
        return "\n".join(lines)

    def clear(self) -> None:
        self._messages.clear()
        self._pending_tool_uses.clear()
        if hasattr(self, "_buffered_results"):
            self._buffered_results.clear()

    def __len__(self) -> int:
        return len(self._messages)
