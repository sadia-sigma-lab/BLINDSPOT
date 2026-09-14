"""Google Gemini API adapter — same interface as BedrockLLMClient.

Supports: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash.
Uses function declarations for tool use.

Set GOOGLE_API_KEY in environment before use.
"""
from __future__ import annotations

import json
import os
from typing import Any


GEMINI_MODEL_MAP = {
    "gemini-2.5-pro":      "gemini-2.5-pro",
    "gemini-2.5-flash":    "gemini-2.5-flash",
    "gemini-2.0-flash":    "gemini-2.0-flash",
    "gemini-1.5-pro":      "gemini-1.5-pro",
    "gemini-1.5-flash":    "gemini-1.5-flash",
    "gemini-pro":          "gemini-1.5-pro",
}


def resolve_gemini_model(model: str) -> str:
    return GEMINI_MODEL_MAP.get(model, model)


class GeminiLLMClient:
    """Google Gemini wrapper with the same .complete() interface as BedrockLLMClient."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        api_key: str | None = None,
    ) -> None:
        self.model_id = resolve_gemini_model(model)
        self.temperature = temperature
        self.max_tokens = max_tokens

        import google.generativeai as genai
        genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self._genai = genai

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Returns the same dict shape as BedrockLLMClient.complete()."""
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool

        # Build Gemini tool definitions
        gemini_tools = None
        if tools:
            fn_decls = []
            for t in tools:
                schema = t.get("input_schema", t.get("parameters", {}))
                fn_decls.append(FunctionDeclaration(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    parameters=schema,
                ))
            gemini_tools = [Tool(function_declarations=fn_decls)]

        # Convert messages to Gemini format
        gemini_history = []
        last_user_msg = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                if isinstance(content, list):
                    parts = []
                    for c in content:
                        if c.get("type") == "text":
                            parts.append(c.get("text", ""))
                        elif c.get("type") == "tool_result":
                            # Gemini expects function response in a specific format
                            parts.append(json.dumps(c.get("content", "")))
                    last_user_msg = "\n".join(parts)
                else:
                    last_user_msg = str(content)

                if gemini_history:
                    gemini_history.append({"role": "user", "parts": [last_user_msg]})

            elif role == "assistant":
                if isinstance(content, list):
                    text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    gemini_history.append({"role": "model", "parts": [" ".join(text_parts)]})
                else:
                    gemini_history.append({"role": "model", "parts": [str(content)]})

        # Final user message is the last one
        if not last_user_msg and messages:
            last_msg = messages[-1]
            content = last_msg.get("content", "")
            if isinstance(content, list):
                last_user_msg = " ".join(c.get("text", "") for c in content if c.get("type") == "text")
            else:
                last_user_msg = str(content)

        try:
            gen_config = genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            model_obj = genai.GenerativeModel(
                model_name=self.model_id,
                system_instruction=system if system else None,
                generation_config=gen_config,
                tools=gemini_tools,
            )

            # Use chat with history for multi-turn
            chat = model_obj.start_chat(history=gemini_history[:-1] if gemini_history else [])
            response = chat.send_message(last_user_msg or "Hello")

            content_blocks = []
            text_parts = []
            tool_calls = []

            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        content_blocks.append({"type": "text", "text": part.text})
                        text_parts.append(part.text)
                    elif hasattr(part, "function_call") and part.function_call.name:
                        fc = part.function_call
                        inp = dict(fc.args) if fc.args else {}
                        tc_id = f"fc_{fc.name}_{len(tool_calls)}"
                        content_blocks.append({
                            "type": "tool_use",
                            "id": tc_id,
                            "name": fc.name,
                            "input": inp,
                        })
                        tool_calls.append({"id": tc_id, "name": fc.name, "input": inp})

            stop_reason = "tool_use" if tool_calls else "end_turn"

            return {
                "content_blocks": content_blocks,
                "stop_reason": stop_reason,
                "text": " ".join(text_parts),
                "tool_calls": tool_calls,
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "error": None,
            }

        except Exception as exc:
            return {
                "content_blocks": [],
                "stop_reason": "error",
                "text": "",
                "tool_calls": [],
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
