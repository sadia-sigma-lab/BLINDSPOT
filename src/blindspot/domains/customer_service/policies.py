"""Customer service authorization engine."""
from blindspot.domains.minimal_workspace.policies import (
    AuthorizationEngine as BaseAuthEngine,
    AuthorizationContext,
    AuthorizationDecision,
)


class CustomerServiceAuthorizationEngine(BaseAuthEngine):
    """Customer service engine — adds large-refund approval enforcement."""

    def evaluate(self, bundle, context: AuthorizationContext) -> AuthorizationDecision:
        # Refunds above $500 require approver_id="user_cs_manager"
        if context.action == "refund":
            amount = context.attributes.get("refund_amount", 0.0)
            if amount and float(amount) > 500.0:
                # Check for a valid approval from user_cs_manager
                from datetime import datetime, timezone
                now = context.current_time
                approval_found = False
                for aid, approval in bundle.approvals.items():
                    if (
                        approval.status == "approved"
                        and approval.approver_id == "user_cs_manager"
                        and approval.action == "refund"
                        and (approval.resource_id is None or approval.resource_id == context.resource_id)
                        and approval.requester_id == context.actor_id
                        and approval.is_valid_at(now)
                    ):
                        approval_found = True
                        break
                if not approval_found:
                    return AuthorizationDecision(
                        allowed=False,
                        decision="require_approval",
                        reasons=[
                            f"Refunds > $500 require approval from user_cs_manager "
                            f"(requested amount: {amount})"
                        ],
                    )
        return super().evaluate(bundle, context)
