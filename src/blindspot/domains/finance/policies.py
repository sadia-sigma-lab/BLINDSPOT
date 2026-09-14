"""Finance authorization engine."""
from blindspot.domains.minimal_workspace.policies import (
    AuthorizationEngine as BaseAuthEngine,
    AuthorizationContext,
    AuthorizationDecision,
)


class FinanceAuthorizationEngine(BaseAuthEngine):
    """Finance engine adds self-approval denial."""

    def evaluate(self, bundle, context):
        # Deny self-approval for transfers
        if context.action == "approve" and context.attributes.get("payment_initiator") == context.actor_id:
            return AuthorizationDecision(
                allowed=False,
                decision="deny",
                reasons=["Self-approval denied for payment transfers"],
            )
        return super().evaluate(bundle, context)
