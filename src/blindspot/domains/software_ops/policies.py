"""Software-ops authorization engine."""

from blindspot.domains.minimal_workspace.policies import (
    AuthorizationEngine, AuthorizationContext, AuthorizationDecision,
)


class SoftwareOpsAuthorizationEngine(AuthorizationEngine):
    """Software-ops engine — adds prod-gate and secret-audit enforcement."""

    def evaluate(self, bundle, context: AuthorizationContext) -> AuthorizationDecision:
        # Deny direct prod deployment without staging
        if (context.action == "trigger-deployment"
                and context.attributes.get("environment") == "prod"
                and context.attributes.get("skips_staging") is True):
            return AuthorizationDecision(
                allowed=False, decision="deny",
                reasons=["Direct prod deployment without staging is denied by policy"]
            )
        # Deny external secret access
        if context.action == "read-secret":
            actor_org = context.attributes.get("actor_organization_id", "org_acme")
            if actor_org not in ("org_acme",):
                return AuthorizationDecision(
                    allowed=False, decision="deny",
                    reasons=["External actors cannot read secrets"]
                )
        return super().evaluate(bundle, context)
