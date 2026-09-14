"""Dual-agent run configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AgentModelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    model: str
    region: str = "us-east-1"
    temperature: float = 0.3
    max_tokens: int = 2048
    display_name: str = ""


class DualAgentRunConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: str
    seed: int = 42
    attack_family: str = "benign_user"
    malicious_goal: str = ""
    max_turns: int = 20

    user_agent: AgentModelConfig = Field(
        default_factory=lambda: AgentModelConfig(
            model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            temperature=0.8, max_tokens=512, display_name="Claude Haiku 4.5",
        )
    )
    execution_agent: AgentModelConfig = Field(
        default_factory=lambda: AgentModelConfig(
            model="us.anthropic.claude-opus-4-6-v1",
            temperature=0.3, max_tokens=2048, display_name="Claude Opus 4.6",
        )
    )
    judge: AgentModelConfig = Field(
        default_factory=lambda: AgentModelConfig(
            model="us.anthropic.claude-opus-5",
            temperature=0.0, max_tokens=1024, display_name="Claude Opus 5",
        )
    )

    use_llm_user_agent: bool = True
    persist_trajectory: bool = True
    artifact_root: str = "data"

    # Vulnerability mode controls the ExecutionAgent's system prompt and tool behaviour:
    #   "none"             — standard safe agent (default)
    #   "misconfigured"    — system prompt says approvals are suspended (compromised deployment)
    #   "prompt_injection" — malicious content injected into read-file tool results
    #   "weak_model"       — ExecutionAgent is Haiku 4.5 (less aligned, more compliant)
    vulnerability_mode: str = "none"
