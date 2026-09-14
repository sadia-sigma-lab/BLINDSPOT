# Permissions and Approvals

## Permission Records

Bind a subject (user/group/role/agent) to a resource and permission name. Support time windows (`valid_from`, `valid_until`) and conditions.

## Approval Records

Required when a policy has `effect: require_approval`. An approval is bound to a specific `(action, resource_id, target_id)` tuple and expires at `valid_until`.

## Authorization Engine

`AuthorizationEngine.evaluate(bundle, context)` returns `AuthorizationDecision` with:
- `allowed: bool`
- `decision`: allow | deny | require_approval | require_verification
- matched permission, approval, and policy IDs
- human-readable reasons
