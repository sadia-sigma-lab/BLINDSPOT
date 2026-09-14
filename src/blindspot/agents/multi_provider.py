"""Multi-provider LLM client factory.

Routes model IDs to the correct backend:
  - Bedrock (Claude, Llama, Mistral, Nova, …)
  - OpenAI  (gpt-3.5-turbo, gpt-4o, gpt-4.5, …)
  - Gemini  (gemini-2.5-pro, gemini-1.5-*, …)

Usage:
    from blindspot.agents.multi_provider import get_llm_client
    client = get_llm_client("gpt-4o", temperature=0.3)
    result = client.complete(messages, system=..., tools=...)
"""
from __future__ import annotations

import os
from typing import Any


# Models routed to direct OpenAI API (not Bedrock)
_OPENAI_DIRECT = ("gpt-3.5-turbo", "gpt-4.5", "gpt-4o", "gpt-4o-mini",
                  "gpt-4-turbo", "o1", "o3", "o4-mini", "text-davinci")

# Models routed to direct Google API (not Bedrock)
_GEMINI_DIRECT = ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro",
                  "gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro")

# Models on Bedrock that look like OpenAI/Google — route to Bedrock, not direct API
_BEDROCK_GPT   = ("gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.6-sol",
                  "gpt-oss-120b", "gpt-oss-20b")
_BEDROCK_GEMMA = ("gemma-3-27b", "gemma-3-12b", "gemma-3-4b")


def _is_openai(model: str) -> bool:
    m = model.lower()
    return m in _OPENAI_DIRECT or any(m.startswith(p) for p in ("o1", "o3", "o4-")) and m not in _BEDROCK_GPT


def _is_gemini(model: str) -> bool:
    m = model.lower()
    return m in _GEMINI_DIRECT


def get_llm_client(
    model: str,
    region: str = "us-east-1",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    openai_api_key: str | None = None,
    google_api_key: str | None = None,
) -> Any:
    """Return the appropriate LLM client for the given model ID.

    Args:
        model: Model identifier string (e.g. "gpt-4o", "gemini-2.5-pro", "claude-opus-4-6").
        region: AWS region (Bedrock only).
        temperature: Sampling temperature.
        max_tokens: Max output tokens.
        openai_api_key: Override OPENAI_API_KEY env var.
        google_api_key: Override GOOGLE_API_KEY env var.

    Returns:
        A client object with a .complete(messages, system, tools) → dict method.
    """
    if _is_openai(model):
        key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise EnvironmentError(
                f"OPENAI_API_KEY not set. Export it to use {model}."
            )
        from blindspot.agents.openai_adapter import OpenAILLMClient
        return OpenAILLMClient(model=model, temperature=temperature,
                               max_tokens=max_tokens, api_key=key)

    if _is_gemini(model):
        key = google_api_key or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise EnvironmentError(
                f"GOOGLE_API_KEY not set. Export it to use {model}."
            )
        from blindspot.agents.gemini_adapter import GeminiLLMClient
        return GeminiLLMClient(model=model, temperature=temperature,
                               max_tokens=max_tokens, api_key=key)

    # Default: AWS Bedrock
    from blindspot.agents.bedrock_tool_adapter import BedrockLLMClient
    return BedrockLLMClient(model=model, region=region,
                            temperature=temperature, max_tokens=max_tokens)


# ── Display name helpers ────────────────────────────────────────────────────

MODEL_DISPLAY_NAMES = {
    # OpenAI direct API
    "gpt-3.5-turbo":   "GPT-3.5 Turbo",
    "gpt-4.5":         "GPT-4.5",
    "gpt-4.5-preview": "GPT-4.5",
    "gpt-4o":          "GPT-4o",
    "gpt-4o-mini":     "GPT-4o Mini",
    # OpenAI via Bedrock
    "gpt-5.6-terra":   "GPT-5.6 Terra",
    "gpt-5.6-luna":    "GPT-5.6 Luna",
    "gpt-5.6-sol":     "GPT-5.6 Sol",
    "gpt-oss-120b":    "GPT-OSS 120B",
    "gpt-oss-20b":     "GPT-OSS 20B",
    # Gemini direct API
    "gemini-2.5-pro":  "Gemini 2.5 Pro",
    "gemini-2.5-flash":"Gemini 2.5 Flash",
    "gemini-1.5-pro":  "Gemini 1.5 Pro",
    # Google Gemma via Bedrock
    "gemma-3-27b":     "Gemma 3 27B",
    "gemma-3-12b":     "Gemma 3 12B",
    # Claude (Bedrock)
    "claude-opus-4-6":  "Claude Opus 4.6",
    "claude-haiku-4-5": "Claude Haiku 4.5",
    "claude-sonnet-4-6":"Claude Sonnet 4.6",
    # Mistral
    "mistral-large-3":  "Mistral Large 3",
    # Llama / Meta
    "llama3-3-70b":     "Llama-3.3-70B",
}


def display_name(model: str) -> str:
    return MODEL_DISPLAY_NAMES.get(model, model)


def normalize_model_key(model: str) -> str:
    """Canonical short key for storage/metrics (no version suffixes)."""
    m = model.lower()
    if "opus-4-6" in m or m == "claude-opus-4-6":   return "claude-opus-4-6"
    if "haiku-4-5" in m:                             return "claude-haiku-4-5"
    if "sonnet-4-6" in m:                            return "claude-sonnet-4-6"
    if "mistral-large-3" in m:                       return "mistral-large-3"
    if "llama3-3" in m or "llama3_3" in m:           return "llama3-3-70b"
    if "gpt-3.5" in m:                               return "gpt-3.5-turbo"
    if "gpt-4.5" in m:                               return "gpt-4.5"
    if "gpt-4o" in m and "mini" not in m:            return "gpt-4o"
    if "gpt-4o-mini" in m:                           return "gpt-4o-mini"
    if "gemini-2.5-pro" in m:                        return "gemini-2.5-pro"
    if "gemini-2.5-flash" in m:                      return "gemini-2.5-flash"
    return model
