"""E-commerce authorization engine."""
from blindspot.domains.minimal_workspace.policies import (
    AuthorizationEngine,
    AuthorizationContext,
    AuthorizationDecision,
)


class EcommerceAuthorizationEngine(AuthorizationEngine):
    """E-commerce engine — pass-through with base permission checks."""

    def evaluate(self, bundle, context: AuthorizationContext) -> AuthorizationDecision:
        return super().evaluate(bundle, context)
