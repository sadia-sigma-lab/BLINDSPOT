# Authorization and Approvals in Tools

## Flow

1. `build_authorization_context()` extracts resource, target, and attributes from tool arguments
2. `AuthorizationEngine.evaluate(bundle, context)` checks permissions → policies → approvals
3. Result: `allow`, `deny`, `require_approval`, or `require_verification`

## Approval requirement

When a policy rule has `effect: require_approval`, the engine checks `bundle.approvals` for a valid `ApprovalRecord` that:
- Is `status="approved"` and not expired
- Covers the exact `(action, resource_id, target_id)` tuple

## External target detection

`build_authorization_context` marks `attributes["external_target"]=True` when the target email doesn't appear in known-user emails, triggering external-sharing policy rules.
