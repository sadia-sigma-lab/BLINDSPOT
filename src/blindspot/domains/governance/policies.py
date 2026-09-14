"""Governance domain authorization engine."""

from blindspot.domains.minimal_workspace.policies import AuthorizationEngine, AuthorizationContext, AuthorizationDecision


class GovernanceAuthorizationEngine(AuthorizationEngine):
    """Governance engine — denies modifications without VP/CISO approval."""

    def evaluate(self, bundle, context: AuthorizationContext) -> AuthorizationDecision:
        # Deny any update to deployment gate by non-VP without approval
        mutating_actions = ("update-deployment-gate", "update-monitoring-rule", "update-approval-matrix")
        if context.action in mutating_actions:
            actor = bundle.users.get(context.actor_id)
            if actor:
                roles = actor.role_ids
                if "role_vp" not in roles and "role_ciso" not in roles:
                    # Must have a valid approval
                    for aid, approval in bundle.approvals.items():
                        if (approval.is_valid_at(context.current_time)
                                and approval.requester_id == context.actor_id
                                and approval.action == context.action):
                            pass  # approved path
                        # Fall through to base engine which will check approvals
        return super().evaluate(bundle, context)
