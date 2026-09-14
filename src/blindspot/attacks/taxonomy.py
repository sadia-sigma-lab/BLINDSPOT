"""Multi-axis attack taxonomy enumerations."""

from enum import Enum


class AttackSource(str, Enum):
    USER = "user"
    ENVIRONMENT = "environment"
    TOOL = "tool"
    MEMORY = "memory"
    AGENT = "agent"
    EVENT = "event"
    BACKGROUND_ACTOR = "background_actor"


class AttackTarget(str, Enum):
    INTENT = "intent"
    PLAN = "plan"
    TOOL_SELECTION = "tool_selection"
    TOOL_ARGUMENTS = "tool_arguments"
    AUTHORIZATION = "authorization"
    OBSERVATION = "observation"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    STATE_BELIEF = "state_belief"
    RECOVERY = "recovery"


class AttackMechanism(str, Enum):
    DIRECT_INSTRUCTION = "direct_instruction"
    INDIRECT_INJECTION = "indirect_injection"
    SOCIAL_ENGINEERING = "social_engineering"
    DECOMPOSITION = "decomposition"
    AUTHORITY_SPOOFING = "authority_spoofing"
    APPROVAL_LAUNDERING = "approval_laundering"
    OUTPUT_SPOOFING = "output_spoofing"
    OBSERVATION_POISONING = "observation_poisoning"
    STATE_CORRUPTION = "state_corruption"
    RETRIEVAL_POISONING = "retrieval_poisoning"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DELAYED_ACTIVATION = "delayed_activation"
    RACE_MANIPULATION = "race_manipulation"
    PROVENANCE_STRIPPING = "provenance_stripping"
    CROSS_AGENT_PROPAGATION = "cross_agent_propagation"


class AttackTemporalPattern(str, Enum):
    ONE_SHOT = "one_shot"
    GRADUAL = "gradual"
    STAGED = "staged"
    DELAYED = "delayed"
    PERSISTENT = "persistent"
    CROSS_SESSION = "cross_session"
    ADAPTIVE = "adaptive"
    OPPORTUNISTIC = "opportunistic"


class AttackHarmCategory(str, Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"
    PRIVACY = "privacy"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    REPUTATIONAL = "reputational"
    LOSS_OF_CONTROL = "loss_of_control"


class AttackerKnowledgeTier(str, Enum):
    STATIC = "static"
    PUBLIC_RESPONSES = "public_responses"
    TOOL_CALLS = "tool_calls"
    PARTIAL_STATE = "partial_state"
    DEFENSE_AWARE = "defense_aware"
    INTERNAL_REASONING = "internal_reasoning"


# Canonical set of known lifecycle hook names
KNOWN_HOOKS = frozenset({
    "before_session", "after_session",
    "before_user_message", "after_user_message",
    "before_observation", "after_observation",
    "before_action", "after_action",
    "before_tool", "after_tool",
    "before_event", "after_event",
    "before_memory_write", "after_memory_write",
    "on_episode_end",
})
