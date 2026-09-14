"""Low-level Bedrock API wrapper with proper native tool-use/tool-result support.

Supports Claude (native tool_use blocks) and open-source models
(Llama, Mistral, DeepSeek, Qwen, Amazon Nova) via the Bedrock Converse API.
Open-source models are used as less-aligned attackers and execution agents
to generate real unsafe_completion trajectories (Boiling the Frog §4: Llama 78.4% ASR).
"""

from __future__ import annotations

import json
import time
import uuid
from enum import Enum
from typing import Any

from blindspot.agents.conversation import ConversationHistory


BEDROCK_DEFAULT_REGION = "us-east-1"


class ModelFamily(str, Enum):
    CLAUDE   = "claude"    # Native tool_use/tool_result content blocks
    LLAMA    = "llama"     # Converse API with toolConfig
    MISTRAL  = "mistral"   # Converse API with toolConfig
    DEEPSEEK = "deepseek"  # Converse API with toolConfig
    QWEN     = "qwen"      # Converse API with toolConfig
    NOVA     = "nova"      # Amazon Converse API


def _detect_family(model_id: str) -> ModelFamily:
    mid = model_id.lower()
    if "claude"   in mid: return ModelFamily.CLAUDE
    if "llama"    in mid: return ModelFamily.LLAMA
    if "mistral"  in mid or "magistral" in mid or "ministral" in mid or "devstral" in mid or "voxtral" in mid:
        return ModelFamily.MISTRAL
    if "deepseek" in mid: return ModelFamily.DEEPSEEK
    if "qwen"     in mid: return ModelFamily.QWEN
    if "nova"     in mid: return ModelFamily.NOVA
    # OpenAI models via Bedrock (gpt-5.6-*, gpt-oss-*) and Google Gemma → Converse API
    if "gpt"      in mid or "gemma" in mid: return ModelFamily.LLAMA
    return ModelFamily.CLAUDE


# Models that do not accept the temperature parameter
_NO_TEMPERATURE_MODELS = (
    "claude-opus-5", "claude-sonnet-5", "claude-fable-5",
    "opus-5", "sonnet-5",
    # OpenAI GPT models via Bedrock
    "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.6-sol",
    "gpt-oss-120b", "gpt-oss-20b",
)

_MODEL_MAP = {
    # ── Claude ─────────────────────────────────────────────────────────────
    "claude-opus-4-6":   "us.anthropic.claude-opus-4-6-v1",
    "claude-opus-5":     "us.anthropic.claude-opus-5",
    "claude-sonnet-4-6": "us.anthropic.claude-sonnet-4-6",
    "claude-haiku-4-5":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "claude-opus-4-7":   "us.anthropic.claude-opus-4-7",
    "claude-opus-4-8":   "us.anthropic.claude-opus-4-8",
    "claude-sonnet-5":   "us.anthropic.claude-sonnet-5",
    # ── Llama (Meta) ───────────────────────────────────────────────────────
    "llama3-3-70b":      "us.meta.llama3-3-70b-instruct-v1:0",
    "llama4-scout-17b":  "us.meta.llama4-scout-17b-instruct-v1:0",
    "llama4-maverick":   "us.meta.llama4-maverick-17b-instruct-v1:0",
    "llama3-1-70b":      "us.meta.llama3-1-70b-instruct-v1:0",
    "llama3-1-8b":       "us.meta.llama3-1-8b-instruct-v1:0",
    # ── Mistral ────────────────────────────────────────────────────────────
    "mistral-large-3":   "mistral.mistral-large-3-675b-instruct",
    "ministral-8b":      "mistral.ministral-3-8b-instruct",
    "ministral-14b":     "mistral.ministral-3-14b-instruct",
    # ── DeepSeek ───────────────────────────────────────────────────────────
    "deepseek-v3":       "deepseek.v3.2",
    # ── Qwen ───────────────────────────────────────────────────────────────
    "qwen3-32b":         "qwen.qwen3-32b-v1:0",
    "qwen3-80b":         "qwen.qwen3-next-80b-a3b",
    # ── Amazon Nova ────────────────────────────────────────────────────────
    "nova-pro":          "amazon.nova-pro-v1:0",
    "nova-lite":         "amazon.nova-lite-v1:0",
    "nova-premier":      "amazon.nova-premier-v1:0",
    # ── OpenAI (via Bedrock inference profiles) ────────────────────────────
    "gpt-5.6-terra":     "us.openai.gpt-5.6-terra",
    "gpt-5.6-luna":      "us.openai.gpt-5.6-luna",
    "gpt-5.6-sol":       "us.openai.gpt-5.6-sol",
    "gpt-oss-120b":      "openai.gpt-oss-120b-1:0",
    "gpt-oss-20b":       "openai.gpt-oss-20b-1:0",
    # ── Google Gemma (via Bedrock) ─────────────────────────────────────────
    "gemma-3-27b":       "google.gemma-3-27b-it",
    "gemma-3-12b":       "google.gemma-3-12b-it",
    "gemma-3-4b":        "google.gemma-3-4b-it",
}


def resolve_model(model: str) -> str:
    return _MODEL_MAP.get(model, model)


class BedrockLLMClient:
    """
    Unified Bedrock wrapper for Claude AND open-source models (Llama, Mistral, DeepSeek).

    Claude uses the Anthropic SDK (AnthropicBedrock) with native tool_use blocks.
    Open-source models use the boto3 Converse API with toolConfig.
    Both return the same dict shape for downstream compatibility.
    """

    def __init__(self, model: str, region: str = BEDROCK_DEFAULT_REGION,
                 temperature: float = 0.3, max_tokens: int = 2048) -> None:
        self.model_id = resolve_model(model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.region = region
        self.family = _detect_family(self.model_id)

        if self.family == ModelFamily.CLAUDE:
            from anthropic import AnthropicBedrock
            self._claude = AnthropicBedrock(aws_region=region)
            self._boto = None
        else:
            import boto3
            self._claude = None
            self._boto = boto3.client("bedrock-runtime", region_name=region)

    def complete(
        self,
        messages: list[dict[str, Any]],
        system: str = "",
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Call the model. Returns a unified dict:
          content_blocks : list of {type, text/id/name/input}
          stop_reason    : "end_turn" | "tool_use" | "max_tokens"
          text           : concatenated text output
          tool_calls     : list of {id, name, input}
          usage          : {input_tokens, output_tokens}
          error          : dict or None
        """
        if self.family == ModelFamily.CLAUDE:
            return self._complete_claude(messages, system, tools)
        else:
            return self._complete_converse(messages, system, tools)

    # ── Claude (Anthropic SDK) ────────────────────────────────────────────────

    def _complete_claude(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            params["system"] = system
        _no_temp = ("claude-opus-5", "claude-sonnet-5", "claude-fable-5")
        if self.temperature != 0.0 and not any(m in self.model_id for m in _no_temp):
            params["temperature"] = self.temperature
        if tools:
            params["tools"] = [self._build_tool_schema(t) for t in tools]

        try:
            t0 = time.monotonic()
            response = self._claude.messages.create(**params)
            latency = (time.monotonic() - t0) * 1000

            # Parse content blocks
            content_blocks: list[dict] = []
            text_parts: list[str] = []
            tool_calls: list[dict] = []

            for block in response.content:
                btype = getattr(block, "type", "")
                if btype == "text":
                    txt = getattr(block, "text", "")
                    content_blocks.append({"type": "text", "text": txt})
                    if txt:
                        text_parts.append(txt)
                elif btype == "tool_use":
                    inp = getattr(block, "input", {})
                    if isinstance(inp, str):
                        try:
                            inp = json.loads(inp)
                        except Exception:
                            inp = {}
                    tid = getattr(block, "id", str(uuid.uuid4()))
                    name = getattr(block, "name", "")
                    content_blocks.append({"type": "tool_use", "id": tid, "name": name, "input": inp})
                    tool_calls.append({"id": tid, "name": name, "input": inp})

            usage: dict[str, Any] = {}
            if hasattr(response, "usage"):
                u = response.usage
                usage = {
                    "input_tokens": getattr(u, "input_tokens", 0),
                    "output_tokens": getattr(u, "output_tokens", 0),
                }

            return {
                "content_blocks": content_blocks,
                "stop_reason": getattr(response, "stop_reason", "end_turn"),
                "text": "\n".join(text_parts).strip(),
                "tool_calls": tool_calls,
                "usage": usage,
                "latency_ms": latency,
                "error": None,
            }

        except Exception as exc:
            err_msg = str(exc)
            if "credentials" in err_msg.lower() or "auth" in err_msg.lower():
                raise RuntimeError(f"AWS Bedrock auth failed: {exc}") from exc
            return {
                "content_blocks": [],
                "stop_reason": "error",
                "text": "",
                "tool_calls": [],
                "usage": {},
                "latency_ms": 0.0,
                "error": {"code": type(exc).__name__, "message": err_msg},
            }

    # ── Open-source models (Boto3 Converse API) ───────────────────────────────

    def _complete_converse(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        """Use the boto3 bedrock-runtime Converse API for Llama/Mistral/etc."""
        # Convert messages to Converse format
        converse_msgs = self._to_converse_messages(messages)
        params: dict[str, Any] = {
            "modelId": self.model_id,
            "messages": converse_msgs,
            "inferenceConfig": {"maxTokens": self.max_tokens},
        }
        if system:
            params["system"] = [{"text": system}]
        _no_temp_converse = _NO_TEMPERATURE_MODELS
        if self.temperature != 0.0 and not any(m in self.model_id for m in _no_temp_converse):
            params["inferenceConfig"]["temperature"] = self.temperature
        if tools:
            params["toolConfig"] = {
                "tools": [self._build_converse_tool(t) for t in tools]
            }

        try:
            t0 = time.monotonic()
            response = self._boto.converse(**params)
            latency = (time.monotonic() - t0) * 1000

            content_blocks: list[dict] = []
            text_parts: list[str] = []
            tool_calls: list[dict] = []

            output_msg = response.get("output", {}).get("message", {})
            for block in output_msg.get("content", []):
                if "text" in block:
                    txt = block["text"]
                    content_blocks.append({"type": "text", "text": txt})
                    if txt:
                        text_parts.append(txt)
                elif "toolUse" in block:
                    tu = block["toolUse"]
                    tid  = tu.get("toolUseId", str(uuid.uuid4()))
                    name = tu.get("name", "")
                    inp  = tu.get("input", {})
                    if isinstance(inp, str):
                        try: inp = json.loads(inp)
                        except Exception: inp = {}
                    content_blocks.append({"type": "tool_use", "id": tid, "name": name, "input": inp})
                    tool_calls.append({"id": tid, "name": name, "input": inp})

            stop_reason_raw = response.get("stopReason", "end_turn")

            # Parse JSON-in-text tool calls (common Llama/open-source pattern):
            # Some models output {"type":"function","name":...} as text
            # even when toolConfig is passed. Detect and promote these.
            if stop_reason_raw != "tool_use" and not tool_calls:
                promoted = self._extract_text_tool_calls(text_parts)
                if promoted:
                    tool_calls = promoted
                    # Replace text blocks with promoted tool_use blocks
                    content_blocks = [
                        b for b in content_blocks if b.get("type") == "text"
                        and not any(c in b.get("text","") for c in ['"type": "function"', '"type":"function"'])
                    ]
                    for tc in promoted:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": tc["id"],
                            "name": tc["name"],
                            "input": tc["input"],
                        })
                    stop_reason_raw = "tool_use"

            stop_reason = "tool_use" if stop_reason_raw == "tool_use" else "end_turn"

            usage_raw = response.get("usage", {})
            usage = {
                "input_tokens":  usage_raw.get("inputTokens", 0),
                "output_tokens": usage_raw.get("outputTokens", 0),
            }
            return {
                "content_blocks": content_blocks,
                "stop_reason": stop_reason,
                "text": "\n".join(text_parts).strip(),
                "tool_calls": tool_calls,
                "usage": usage,
                "latency_ms": latency,
                "error": None,
                "model_family": self.family.value,
            }

        except Exception as exc:
            err_msg = str(exc)
            if "credentials" in err_msg.lower() or "auth" in err_msg.lower():
                raise RuntimeError(f"AWS Bedrock auth failed: {exc}") from exc
            return {
                "content_blocks": [],
                "stop_reason": "error",
                "text": "",
                "tool_calls": [],
                "usage": {},
                "latency_ms": 0.0,
                "error": {"code": type(exc).__name__, "message": err_msg},
                "model_family": self.family.value,
            }

    @staticmethod
    def _extract_text_tool_calls(text_parts: list[str]) -> list[dict]:
        """Extract JSON function calls from text output (Llama/Mistral text-based calling).

        Handles formats:
          {"type": "function", "name": "...", "parameters": {...}}
          {"type": "function_call", "function": {"name": "...", "arguments": "..."}}
        """
        import re as _re
        calls = []
        text = " ".join(text_parts)

        # Find all JSON objects in the text
        for match in _re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}', text, _re.DOTALL):
            try:
                obj = json.loads(match.group())
            except Exception:
                continue

            # Format 1: {"type":"function","name":"...","parameters":{...}}
            if obj.get("type") in ("function", "function_call") and "name" in obj:
                calls.append({
                    "id": str(uuid.uuid4()),
                    "name": obj["name"],
                    "input": obj.get("parameters", obj.get("arguments", obj.get("input", {}))),
                })
            # Format 2: {"function":{"name":"...","arguments":"..."}}
            elif "function" in obj and isinstance(obj["function"], dict):
                fn = obj["function"]
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except Exception: args = {}
                calls.append({
                    "id": str(uuid.uuid4()),
                    "name": fn.get("name", ""),
                    "input": args,
                })

        return calls

    @staticmethod
    def _to_converse_messages(messages: list[dict]) -> list[dict]:
        """Convert Anthropic-format messages to Bedrock Converse format."""
        result = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, str):
                result.append({"role": role, "content": [{"text": content}]})
            elif isinstance(content, list):
                converse_content = []
                for block in content:
                    btype = block.get("type", "")
                    if btype == "text":
                        converse_content.append({"text": block.get("text", "")})
                    elif btype == "tool_use":
                        converse_content.append({"toolUse": {
                            "toolUseId": block.get("id", str(uuid.uuid4())),
                            "name": block.get("name", ""),
                            "input": block.get("input", {}),
                        }})
                    elif btype == "tool_result":
                        raw = block.get("content", "")
                        text_val = json.dumps(raw, default=str) if isinstance(raw, (dict, list)) else str(raw)
                        converse_content.append({"toolResult": {
                            "toolUseId": block.get("tool_use_id", ""),
                            "content": [{"text": text_val}],
                            "status": "error" if block.get("is_error") else "success",
                        }})
                if converse_content:
                    result.append({"role": role, "content": converse_content})
            else:
                result.append({"role": role, "content": [{"text": str(content)}]})
        return result

    @staticmethod
    def _build_converse_tool(tool: dict[str, Any]) -> dict[str, Any]:
        """Convert to Bedrock Converse toolSpec format."""
        name = tool.get("name", "")
        desc = tool.get("description", "")
        schema = tool.get("parameters", tool.get("input_schema", {"type": "object", "properties": {}}))
        if "function" in tool:
            fn = tool["function"]
            name = fn.get("name", name)
            desc = fn.get("description", desc)
            schema = fn.get("parameters", schema)
        return {"toolSpec": {"name": name, "description": desc, "inputSchema": {"json": schema}}}

    @staticmethod
    def _build_tool_schema(tool: dict[str, Any]) -> dict[str, Any]:
        """Claude (Anthropic SDK) tool schema format."""
        if "function" in tool:
            fn = tool["function"]
            return {
                "name": fn.get("name", ""),
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            }
        return {
            "name": tool.get("name", ""),
            "description": tool.get("description", ""),
            "input_schema": tool.get("parameters", tool.get("input_schema",
                {"type": "object", "properties": {}})),
        }
