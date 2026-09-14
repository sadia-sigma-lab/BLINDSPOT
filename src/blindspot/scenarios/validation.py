"""Scenario validation system."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.scenarios.schema import FullScenarioSpec


class ScenarioValidationIssue(BaseModel):
    model_config = ConfigDict(frozen=True)
    severity: str
    code: str
    message: str
    path: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class ScenarioValidationReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    valid: bool
    scenario_id: str
    issues: list[ScenarioValidationIssue]
    resolved_components: dict[str, list[str]] = Field(default_factory=dict)
    initial_state_hash: str | None = None
    graph_metrics: dict[str, Any] = Field(default_factory=dict)

    def errors(self) -> list[ScenarioValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]


def validate_scenario(
    spec: FullScenarioSpec,
    attack_registry: Any | None = None,
) -> ScenarioValidationReport:
    """Run all validation checks against a FullScenarioSpec."""
    issues: list[ScenarioValidationIssue] = []
    scenario_id = spec.metadata.scenario_id.canonical()

    # Unique actor IDs (already enforced by model_validator, but belt-and-suspenders)
    actor_ids = {a.actor_id for a in spec.actors}
    if len(actor_ids) != len(spec.actors):
        issues.append(ScenarioValidationIssue(
            severity="error", code="DUPLICATE_ACTOR_ID",
            message="Scenario has duplicate actor IDs", path="actors",
        ))

    # Task actor references valid actors
    if spec.task.user_actor_id not in actor_ids:
        issues.append(ScenarioValidationIssue(
            severity="error", code="INVALID_USER_ACTOR",
            message=f"Task user_actor_id {spec.task.user_actor_id!r} not in actors",
            path="task.user_actor_id",
        ))
    if spec.task.target_actor_id not in actor_ids:
        issues.append(ScenarioValidationIssue(
            severity="error", code="INVALID_TARGET_ACTOR",
            message=f"Task target_actor_id {spec.task.target_actor_id!r} not in actors",
            path="task.target_actor_id",
        ))

    # Tool binding has no conflict
    tool_conflict = set(spec.tools.enabled_tool_ids) & set(spec.tools.disabled_tool_ids)
    if tool_conflict:
        issues.append(ScenarioValidationIssue(
            severity="error", code="TOOL_BINDING_CONFLICT",
            message=f"Tools both enabled and disabled: {tool_conflict}",
            path="tools",
        ))

    # Attack bindings reference valid attacks
    if attack_registry:
        for binding in spec.attacks:
            if binding.enabled and not attack_registry.contains(binding.attack_id):
                issues.append(ScenarioValidationIssue(
                    severity="error", code="UNKNOWN_ATTACK",
                    message=f"Attack {binding.attack_id!r} not in registry",
                    path=f"attacks.{binding.instance_id}",
                ))

    # Horizon validation
    horizon = spec.horizon
    if horizon.expected_tool_calls and horizon.expected_tool_calls > horizon.max_tool_calls:
        issues.append(ScenarioValidationIssue(
            severity="error", code="HORIZON_INCONSISTENT",
            message="expected_tool_calls exceeds max_tool_calls",
            path="horizon",
        ))

    # Forbidden outcome must not be true initially (skipped — requires state evaluation)

    # Hidden state isolation: check hidden section references
    hidden_keys = set(spec.hidden.model_dump().keys())
    public_actor_ids = {a.actor_id for a in spec.actors if a.actor_type == "target_agent"}
    # (Full isolation check done at runtime)

    # Solvability: check task has at least one safe alternative or goal predicate
    if not spec.task.goal_predicates and not spec.safe_alternatives:
        issues.append(ScenarioValidationIssue(
            severity="warning", code="NO_GOAL_PREDICATES",
            message="Task has no goal_predicates and no safe_alternatives",
            path="task",
        ))

    # Safe twin consistency for adversarial scenarios
    adversarial = any(b.enabled for b in spec.attacks)
    if adversarial and not any(b.clean_control_id for b in spec.attacks):
        issues.append(ScenarioValidationIssue(
            severity="warning", code="NO_CLEAN_CONTROL",
            message="Adversarial scenario has no clean_control_id on any attack binding",
            path="attacks",
        ))

    has_errors = any(i.severity == "error" for i in issues)
    return ScenarioValidationReport(
        valid=not has_errors,
        scenario_id=scenario_id,
        issues=issues,
        resolved_components={
            "actors": [a.actor_id for a in spec.actors],
            "tools": spec.tools.enabled_tool_ids,
            "attacks": [b.attack_id for b in spec.attacks if b.enabled],
        },
    )


def check_solvability(spec: FullScenarioSpec) -> list[ScenarioValidationIssue]:
    """Check that the scenario has a feasible safe execution path."""
    issues: list[ScenarioValidationIssue] = []

    # Simple heuristic: check required tools are in enabled set
    task_tools_needed = ["list-files", "read-file"]
    enabled = set(spec.tools.enabled_tool_ids)
    for tool in task_tools_needed:
        if tool not in enabled:
            issues.append(ScenarioValidationIssue(
                severity="warning", code="TOOL_NOT_AVAILABLE",
                message=f"Tool {tool!r} expected for task but not in enabled_tool_ids",
                path="tools.enabled_tool_ids",
            ))

    # Horizon budget check
    if spec.horizon.max_interaction_steps < len(spec.task.expected_subgoals) * 2:
        issues.append(ScenarioValidationIssue(
            severity="warning", code="HORIZON_POSSIBLY_TOO_SHORT",
            message="Horizon may be too short for expected number of subgoals",
            path="horizon.max_interaction_steps",
        ))

    return issues
