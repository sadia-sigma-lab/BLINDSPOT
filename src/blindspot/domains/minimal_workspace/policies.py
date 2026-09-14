"""Authorization engine for the minimal workspace domain."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AuthorizationContext(BaseModel):
    """Runtime context passed to the authorization engine."""

    model_config = ConfigDict(frozen=True)

    actor_id: str
    action: str
    resource_id: str | None = None
    target_id: str | None = None
    step: int
    current_time: datetime
    attributes: dict[str, Any] = Field(default_factory=dict)


class AuthorizationDecision(BaseModel):
    """Structured authorization decision."""

    model_config = ConfigDict(frozen=True)

    allowed: bool
    decision: Literal["allow", "deny", "require_approval", "require_verification"]
    matched_policy_ids: list[str] = Field(default_factory=list)
    matched_permission_ids: list[str] = Field(default_factory=list)
    matched_approval_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class AuthorizationEngine:
    """Evaluates permissions, approvals, and policies to make access decisions."""

    def evaluate(
        self,
        bundle: "DomainStateBundle",  # type: ignore[name-defined]
        context: AuthorizationContext,
    ) -> AuthorizationDecision:
        matched_permissions: list[str] = []
        matched_approvals: list[str] = []
        matched_policies: list[str] = []
        reasons: list[str] = []

        actor = bundle.users.get(context.actor_id)
        actor_groups = actor.group_ids if actor else []
        actor_roles = actor.role_ids if actor else []

        # 1. Collect matching active permissions
        base_allow = False
        for pid, perm in bundle.permissions.items():
            if not perm.is_active_at(context.current_time):
                continue
            if perm.permission != context.action:
                continue
            if context.resource_id and perm.resource_id != context.resource_id:
                continue
            subject_match = (
                (perm.subject_type == "user" and perm.subject_id == context.actor_id)
                or (perm.subject_type == "group" and perm.subject_id in actor_groups)
                or (perm.subject_type == "role" and perm.subject_id in actor_roles)
            )
            if subject_match:
                matched_permissions.append(pid)
                base_allow = True

        # 2. Check tenant boundary (cross-tenant denial)
        if actor and context.resource_id:
            resource = bundle.resources.get(context.resource_id)
            if resource and actor.organization_id != resource.organization_id:
                # Check if there is an explicit cross-tenant permission
                has_cross_tenant = any(
                    bundle.permissions[pid].conditions.get("cross_tenant", False)
                    for pid in matched_permissions
                )
                if not has_cross_tenant:
                    return AuthorizationDecision(
                        allowed=False,
                        decision="deny",
                        reasons=["Cross-tenant access denied"],
                    )

        # 3. Evaluate policy rules (highest priority first)
        sorted_policies = sorted(
            [
                (doc_id, rule)
                for doc_id, doc in bundle.policies.items()
                for rule in doc.rules
                if rule.enabled
            ],
            key=lambda x: -x[1].priority,
        )

        for doc_id, rule in sorted_policies:
            if not self._action_matches(rule.action_pattern, context.action):
                continue
            if not self._resource_conditions_match(rule.resource_conditions, context, bundle):
                continue
            if not self._context_conditions_match(rule.context_conditions, context):
                continue

            matched_policies.append(f"{doc_id}/{rule.rule_id}")

            if rule.effect == "deny":
                return AuthorizationDecision(
                    allowed=False,
                    decision="deny",
                    matched_policy_ids=matched_policies,
                    reasons=[f"Denied by rule {rule.rule_id!r}: {rule.description}"],
                )
            if rule.effect == "require_approval":
                # Check if a valid approval exists
                approval_found = False
                for aid, approval in bundle.approvals.items():
                    if (
                        approval.is_valid_at(context.current_time)
                        and approval.covers(context.action, context.resource_id, context.target_id)
                        and approval.requester_id == context.actor_id
                    ):
                        matched_approvals.append(aid)
                        approval_found = True
                        break
                if not approval_found:
                    return AuthorizationDecision(
                        allowed=False,
                        decision="require_approval",
                        matched_policy_ids=matched_policies,
                        reasons=[f"Approval required by rule {rule.rule_id!r}"],
                    )
            elif rule.effect == "require_verification":
                return AuthorizationDecision(
                    allowed=False,
                    decision="require_verification",
                    matched_policy_ids=matched_policies,
                    reasons=[f"Verification required by rule {rule.rule_id!r}"],
                )
            elif rule.effect == "allow":
                base_allow = True

        if base_allow or matched_approvals:
            return AuthorizationDecision(
                allowed=True,
                decision="allow",
                matched_permission_ids=matched_permissions,
                matched_approval_ids=matched_approvals,
                matched_policy_ids=matched_policies,
                reasons=["Permission granted"],
            )

        return AuthorizationDecision(
            allowed=False,
            decision="deny",
            reasons=["No matching permission found"],
        )

    def _action_matches(self, pattern: str, action: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return action.startswith(pattern[:-1])
        return pattern == action

    def _resource_conditions_match(
        self, conditions: dict, context: AuthorizationContext, bundle: "DomainStateBundle"  # type: ignore[name-defined]
    ) -> bool:
        if not conditions:
            return True
        resource = bundle.resources.get(context.resource_id or "")
        if resource is None:
            return False
        classification_cond = conditions.get("classification", {})
        if "in" in classification_cond:
            if resource.classification not in classification_cond["in"]:
                return False
        return True

    def _context_conditions_match(
        self, conditions: dict, context: AuthorizationContext
    ) -> bool:
        if not conditions:
            return True
        for key, cond in conditions.items():
            value = context.attributes.get(key)
            if "equals" in cond and value != cond["equals"]:
                return False
        return True
