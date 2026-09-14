"""Bridge between the tool runtime and the Skill-02 authorization engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from blindspot.tools.context import ToolExecutionContext
from blindspot.tools.errors import ToolError

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.policies import (
        AuthorizationContext, AuthorizationDecision, AuthorizationEngine,
    )
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
    from blindspot.tools.specification import ToolSpecification
    from blindspot.tools.state_view import ReadOnlyStateView


def build_authorization_context(
    spec: "ToolSpecification",
    args: Any,
    view: "ReadOnlyStateView",
    ctx: ToolExecutionContext,
) -> "AuthorizationContext":
    from blindspot.domains.minimal_workspace.policies import AuthorizationContext

    resource_id: str | None = getattr(args, "file_id", None) or getattr(args, "resource_id", None)
    target_id: str | None = getattr(args, "target_id", None) or getattr(args, "recipient", None)

    # Build context attributes for policy evaluation
    attributes: dict[str, Any] = {}
    if target_id:
        # Heuristic: external if target looks like an email not in known org
        try:
            users = view.get_collection("users") if view.has_scope("users") else {}
            known_emails = {u.get("email", "") for u in users.values() if isinstance(u, dict)}
            if "@" in str(target_id) and target_id not in known_emails:
                attributes["external_target"] = True
        except Exception:
            pass

    # Determine primary action name (use approval_action, then first required_permission, then tool name)
    action = spec.approval_action or (spec.required_permissions[0] if spec.required_permissions else spec.tool_id.name)

    return AuthorizationContext(
        actor_id=ctx.actor_id,
        action=action,
        resource_id=resource_id,
        target_id=target_id,
        step=ctx.step,
        current_time=ctx.current_time,
        attributes=attributes,
    )


def evaluate_authorization(
    engine: "AuthorizationEngine",
    bundle: "DomainStateBundle",
    spec: "ToolSpecification",
    args: Any,
    view: "ReadOnlyStateView",
    ctx: ToolExecutionContext,
) -> tuple["AuthorizationDecision", ToolError | None]:
    """Evaluate authorization and return (decision, error_or_None)."""
    from blindspot.domains.minimal_workspace.policies import AuthorizationDecision as AD

    # Read-only tools with no required permissions are allowed by default
    if not spec.required_permissions and spec.side_effect_level in ("none", "read"):
        decision = AD(allowed=True, decision="allow", reasons=["Read-only tool; no permission required"])
        return decision, None

    auth_ctx = build_authorization_context(spec, args, view, ctx)
    decision = engine.evaluate(bundle, auth_ctx)

    if not decision.allowed:
        if decision.decision == "require_approval":
            return decision, ToolError.approval_required(auth_ctx.action)
        if decision.decision == "require_verification":
            return decision, ToolError(
                code="VERIFICATION_REQUIRED",
                category="authorization",
                message="Verification is required before this action",
                retryable=False,
            )
        return decision, ToolError.authorization()

    return decision, None
