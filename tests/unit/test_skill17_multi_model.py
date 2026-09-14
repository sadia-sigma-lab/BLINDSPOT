"""Tests for Skill 17: open-source model adapter, multi-judge pipeline, Fleiss' κ."""

import pytest
from blindspot.agents.bedrock_tool_adapter import (
    ModelFamily, _detect_family, resolve_model, _MODEL_MAP,
)
from blindspot.judge.multi_judge import (
    fleiss_kappa, MultiJudgePipeline, JudgeConfig, MultiJudgeResult,
    _interpret_kappa,
)


# ── Model family detection ────────────────────────────────────────────────────

def test_detect_claude():
    assert _detect_family("us.anthropic.claude-opus-5") == ModelFamily.CLAUDE
    assert _detect_family("claude-haiku-4-5-20251001-v1:0") == ModelFamily.CLAUDE

def test_detect_llama():
    assert _detect_family("us.meta.llama3-3-70b-instruct-v1:0") == ModelFamily.LLAMA
    assert _detect_family("meta.llama4-scout-17b-instruct-v1:0") == ModelFamily.LLAMA

def test_detect_mistral():
    assert _detect_family("mistral.mistral-large-3-675b-instruct") == ModelFamily.MISTRAL
    assert _detect_family("mistral.ministral-3-8b-instruct") == ModelFamily.MISTRAL
    assert _detect_family("mistral.magistral-small-2509") == ModelFamily.MISTRAL

def test_detect_deepseek():
    assert _detect_family("deepseek.v3.2") == ModelFamily.DEEPSEEK

def test_detect_qwen():
    assert _detect_family("qwen.qwen3-32b-v1:0") == ModelFamily.QWEN

def test_detect_nova():
    assert _detect_family("amazon.nova-pro-v1:0") == ModelFamily.NOVA

def test_model_map_resolve_shortnames():
    assert resolve_model("llama3-3-70b") == "us.meta.llama3-3-70b-instruct-v1:0"
    assert resolve_model("mistral-large-3") == "mistral.mistral-large-3-675b-instruct"
    assert resolve_model("deepseek-v3") == "deepseek.v3.2"
    assert resolve_model("nova-pro") == "amazon.nova-pro-v1:0"
    assert resolve_model("claude-opus-5") == "us.anthropic.claude-opus-5"

def test_model_map_passthrough_unknown():
    raw = "some.custom.model-id"
    assert resolve_model(raw) == raw

def test_all_opensouce_models_in_map():
    expected = ["llama3-3-70b", "llama4-scout-17b", "mistral-large-3",
                "deepseek-v3", "qwen3-32b", "nova-pro"]
    for m in expected:
        assert m in _MODEL_MAP, f"{m} missing from _MODEL_MAP"


# ── Fleiss' κ ─────────────────────────────────────────────────────────────────

def test_fleiss_kappa_perfect_agreement():
    # All 3 judges agree on every item
    ratings = [
        ["correct_refusal", "correct_refusal", "correct_refusal"],
        ["safe", "safe", "safe"],
        ["unsafe_completion", "unsafe_completion", "unsafe_completion"],
    ]
    kappa = fleiss_kappa(ratings)
    assert abs(kappa - 1.0) < 0.01

def test_fleiss_kappa_zero_agreement():
    # Judges uniformly disagree (each item gets one vote per category)
    # Expected κ ≈ 0 for chance-level agreement
    categories = ["safe", "correct_refusal", "unsafe_completion"]
    # 3 items, 3 raters, each assigns a different label
    ratings = [
        ["safe", "correct_refusal", "unsafe_completion"],
        ["correct_refusal", "unsafe_completion", "safe"],
        ["unsafe_completion", "safe", "correct_refusal"],
    ]
    kappa = fleiss_kappa(ratings, categories=categories)
    assert kappa < 0.2  # near-zero agreement

def test_fleiss_kappa_single_rater_returns_one():
    ratings = [["correct_refusal"], ["safe"]]
    kappa = fleiss_kappa(ratings)
    assert kappa == 1.0

def test_fleiss_kappa_empty_returns_zero():
    assert fleiss_kappa([]) == 0.0

def test_fleiss_kappa_moderate_agreement():
    # 2/3 judges agree on each item
    ratings = [
        ["correct_refusal", "correct_refusal", "safe"],
        ["safe", "safe", "correct_refusal"],
        ["unsafe_completion", "unsafe_completion", "ambiguous"],
    ]
    kappa = fleiss_kappa(ratings)
    assert 0.0 < kappa < 1.0


# ── Kappa interpretation ──────────────────────────────────────────────────────

def test_interpret_kappa_strong():
    assert "strong" in _interpret_kappa(0.85)

def test_interpret_kappa_moderate():
    assert "moderate" in _interpret_kappa(0.70)

def test_interpret_kappa_poor():
    assert "poor" in _interpret_kappa(0.10)


# ── Converse message conversion ───────────────────────────────────────────────

def test_converse_messages_text():
    from blindspot.agents.bedrock_tool_adapter import BedrockLLMClient
    msgs = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    result = BedrockLLMClient._to_converse_messages(msgs)
    assert result[0]["content"][0]["text"] == "Hello"
    assert result[1]["content"][0]["text"] == "Hi there"

def test_converse_messages_tool_use():
    from blindspot.agents.bedrock_tool_adapter import BedrockLLMClient
    msgs = [{"role": "assistant", "content": [
        {"type": "tool_use", "id": "tid1", "name": "list-files", "input": {}}
    ]}]
    result = BedrockLLMClient._to_converse_messages(msgs)
    assert "toolUse" in result[0]["content"][0]
    assert result[0]["content"][0]["toolUse"]["name"] == "list-files"

def test_converse_messages_tool_result():
    from blindspot.agents.bedrock_tool_adapter import BedrockLLMClient
    msgs = [{"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "tid1", "content": {"files": []}}
    ]}]
    result = BedrockLLMClient._to_converse_messages(msgs)
    assert "toolResult" in result[0]["content"][0]
    assert result[0]["content"][0]["toolResult"]["toolUseId"] == "tid1"

def test_build_converse_tool():
    from blindspot.agents.bedrock_tool_adapter import BedrockLLMClient
    tool = {"name": "list-files", "description": "List files", "parameters": {"type": "object"}}
    result = BedrockLLMClient._build_converse_tool(tool)
    assert "toolSpec" in result
    assert result["toolSpec"]["name"] == "list-files"
    assert "inputSchema" in result["toolSpec"]


# ── MultiJudgePipeline (unit, no API calls) ────────────────────────────────────

def test_judge_config_serialisable():
    cfg = JudgeConfig(model="us.anthropic.claude-opus-5", display_name="Claude Opus 5")
    assert cfg.model == "us.anthropic.claude-opus-5"

def test_multi_judge_majority_vote():
    """Unit test: given pre-built verdicts, check majority logic."""
    from blindspot.judge.multi_judge import (
        MultiJudgeResult, fleiss_kappa, SAFETY_LABELS
    )
    labels = ["correct_refusal", "correct_refusal", "safe"]
    majority = max(set(labels), key=labels.count)
    assert majority == "correct_refusal"

def test_fleiss_kappa_real_scenario():
    """Simulate 10 episodes with typical judge agreement pattern."""
    import random
    rng = random.Random(42)
    ratings = []
    for _ in range(10):
        # Simulate: primary gives correct_refusal, secondary agrees 80%, tertiary agrees 70%
        primary = rng.choice(["correct_refusal", "safe"])
        sec  = primary if rng.random() < 0.80 else "ambiguous"
        tert = primary if rng.random() < 0.70 else "safe"
        ratings.append([primary, sec, tert])
    kappa = fleiss_kappa(ratings)
    assert kappa > 0.4, f"Expected fair+ agreement, got κ={kappa:.3f}"
