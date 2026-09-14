"""Abstract PythonTool base class with the canonical execution pipeline."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff
from blindspot.tools.arguments import pydantic_to_tool_schema, validate_arguments
from blindspot.tools.audit import build_audit_record
from blindspot.tools.authorization import evaluate_authorization
from blindspot.tools.context import ToolExecutionContext, ToolRuntimeDependencies
from blindspot.tools.errors import ToolError
from blindspot.tools.events import EventEmitter
from blindspot.tools.mutation import MutationPlan
from blindspot.tools.result import ToolExecutionResult
from blindspot.tools.specification import ToolSpecification
from blindspot.tools.state_view import ReadOnlyStateView
from blindspot.tools.transaction import _hash_public

ArgsT = TypeVar("ArgsT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class PythonTool(Generic[ArgsT, OutputT], ABC):
    """Abstract base for all benchmark Python tools."""

    specification: ToolSpecification
    args_model: type[ArgsT]
    output_model: type[OutputT]

    def schema(self) -> dict[str, Any]:
        return pydantic_to_tool_schema(
            self.args_model,
            name=self.specification.tool_id.name,
            description=self.specification.description,
        )

    def validate_arguments(self, raw: dict[str, Any]) -> tuple[ArgsT | None, ToolError | None]:
        return validate_arguments(self.args_model, raw)

    @abstractmethod
    def read(
        self,
        view: ReadOnlyStateView,
        args: ArgsT,
        context: ToolExecutionContext,
    ) -> Any:
        """Read from state; no side effects allowed here."""
        ...

    @abstractmethod
    def plan_mutations(
        self,
        view: ReadOnlyStateView,
        args: ArgsT,
        context: ToolExecutionContext,
    ) -> MutationPlan:
        """Declare all intended state changes; no live mutations here."""
        ...

    def _get_bundle(self, state: WorldState) -> Any:
        """Build a DomainStateBundle from WorldState for authorization queries."""
        from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle
        from blindspot.data_model.user import UserRecord
        from blindspot.data_model.resource import ResourceRecord
        from blindspot.data_model.permission import PermissionRecord
        from blindspot.data_model.approval import ApprovalRecord
        from blindspot.data_model.policy import PolicyDocument

        bundle = DomainStateBundle()

        for uid, u in state.public.get("users", {}).items():
            try:
                bundle.users[uid] = UserRecord(**u)
            except Exception:
                pass

        for rid, r in state.public.get("resources", {}).items():
            try:
                bundle.resources[rid] = ResourceRecord(**r)
            except Exception:
                pass

        for pid, p in state.public.get("permissions", {}).items():
            try:
                bundle.permissions[pid] = PermissionRecord(**p)
            except Exception:
                pass

        for aid, a in state.public.get("approvals", {}).items():
            try:
                bundle.approvals[aid] = ApprovalRecord(**a)
            except Exception:
                pass

        for pol_id, pol in state.public.get("policies", {}).items():
            try:
                bundle.policies[pol_id] = PolicyDocument(**pol)
            except Exception:
                pass

        return bundle

    def execute(
        self,
        state: WorldState,
        raw_arguments: dict[str, Any],
        context: ToolExecutionContext,
        dependencies: ToolRuntimeDependencies,
    ) -> tuple[WorldState, ToolExecutionResult]:
        """Run the full 19-step pipeline; return (new_state, result)."""
        tool_id_str = self.specification.tool_id.canonical()
        pre_hash = _hash_public(state.public)
        _empty_diff = StateDiff(mutations=[])

        def _fail(error: ToolError, new_state: WorldState = state) -> tuple[WorldState, ToolExecutionResult]:
            audit_id = _emit_audit("failure", pre_hash, pre_hash, [], [], False,
                                   error_code=error.code)
            return new_state, ToolExecutionResult(
                tool_call_id=context.tool_call_id,
                tool_id=tool_id_str,
                success=False,
                error=error,
                pre_state_hash=pre_hash,
                post_state_hash=pre_hash,
                audit_ids=[audit_id],
            )

        def _emit_audit(
            result: str,
            pre: str,
            post: str,
            target_ids: list[str],
            event_ids: list[str],
            idempotent: bool,
            policy_decision: str | None = None,
            rollback_ref: str | None = None,
            error_code: str | None = None,
        ) -> str:
            record = build_audit_record(
                ctx=context, tool_id=tool_id_str, raw_args=raw_arguments,
                target_ids=target_ids, result=result,
                policy_decision=policy_decision,
                diff_hash=post if post != pre else None,
                event_ids=event_ids, error_code=error_code,
                rollback_ref=rollback_ref, idempotent=idempotent,
            )
            return dependencies.audit_sink.append(record)

        # 1. Validate arguments
        args, arg_error = self.validate_arguments(raw_arguments)
        if arg_error:
            return _fail(arg_error)

        # 2. Idempotency check
        idem_key = context.idempotency_key
        if idem_key and self.specification.idempotent:
            record, idem_error = dependencies.idempotency_store.check(
                idem_key, context.actor_id, tool_id_str, raw_arguments
            )
            if idem_error:
                return _fail(idem_error)
            if record:
                stored = record.result_snapshot
                return state, ToolExecutionResult(
                    tool_call_id=context.tool_call_id, tool_id=tool_id_str,
                    success=stored.get("success", True), output=stored.get("output"),
                    pre_state_hash=pre_hash, post_state_hash=pre_hash,
                    idempotent_replay=True,
                )

        # 3. Pre-authorization failure check
        should_fail, profile = dependencies.failure_model.should_fail(
            tool_id_str, "before_authorization", context.seed, context.step
        )
        if should_fail and profile:
            return _fail(dependencies.failure_model.build_error(profile))

        # 4. Create scoped read-only view
        view = ReadOnlyStateView(state, frozenset(self.specification.read_scopes))

        # 5. Authorization
        bundle = self._get_bundle(state)
        decision, auth_error = evaluate_authorization(
            dependencies.authorization_engine, bundle, self.specification, args, view, context
        )
        decision_str = decision.decision if decision else "unknown"
        if auth_error:
            _emit_audit("failure", pre_hash, pre_hash, [], [], False,
                        policy_decision=decision_str, error_code=auth_error.code)
            return state, ToolExecutionResult(
                tool_call_id=context.tool_call_id, tool_id=tool_id_str,
                success=False, error=auth_error,
                pre_state_hash=pre_hash, post_state_hash=pre_hash,
                authorization_decision=decision_str,
            )

        # 6. Pre-execution failure
        should_fail, profile = dependencies.failure_model.should_fail(
            tool_id_str, "before_execution", context.seed, context.step
        )
        if should_fail and profile:
            return _fail(dependencies.failure_model.build_error(profile))

        # 7. Read phase
        try:
            read_output = self.read(view, args, context)
        except Exception as exc:
            return _fail(ToolError.internal(str(exc)))

        # 8. Mutation plan
        try:
            plan = self.plan_mutations(view, args, context)
        except Exception as exc:
            return _fail(ToolError.internal(str(exc)))

        # 9. Validate write scopes
        scope_error = view.validate_write_scopes(
            plan.affected_collections(), self.specification.write_scopes
        )
        if scope_error:
            return _fail(scope_error)

        # 10. Pre-commit failure
        should_fail, profile = dependencies.failure_model.should_fail(
            tool_id_str, "before_commit", context.seed, context.step
        )
        if should_fail and profile:
            return _fail(dependencies.failure_model.build_error(profile))

        # 11. Transaction
        new_state = state
        tx_result = None
        event_ids: list[str] = []
        rollback_token: str | None = None

        if not plan.is_empty:
            new_state, tx_result = dependencies.transaction_manager.commit(
                state, plan, self.specification.write_scopes, bundle
            )
            if not tx_result.committed:
                errors_str = "; ".join(
                    i.message for i in tx_result.validation_report.errors()
                )
                return _fail(ToolError(
                    code="TRANSACTION_FAILED", category="internal",
                    message=f"Transaction failed: {errors_str}", retryable=False,
                ))

            # Rollback token
            if self.specification.reversible:
                rollback_token = dependencies.rollback_manager.create_token(
                    tx_result, tool_id_str, context.actor_id
                )

        # 12. Post-commit failure (state already committed)
        should_fail, profile = dependencies.failure_model.should_fail(
            tool_id_str, "after_commit", context.seed, context.step
        )
        if should_fail and profile and profile.failure_type != "false_success":
            err = dependencies.failure_model.build_error(profile)
            audit_id = _emit_audit("failure", pre_hash, pre_hash, [], [], False,
                                   policy_decision=decision_str, error_code=err.code)
            return new_state, ToolExecutionResult(
                tool_call_id=context.tool_call_id, tool_id=tool_id_str,
                success=False, error=err,
                state_diff=tx_result.state_diff if tx_result else _empty_diff,
                pre_state_hash=pre_hash,
                post_state_hash=tx_result.post_state_hash if tx_result else pre_hash,
                audit_ids=[audit_id],
                authorization_decision=decision_str,
                internal_truth={"committed": True},
            )

        # 13. Emit events
        if plan.events:
            emitter = EventEmitter(dependencies.event_queue)
            event_ids = emitter.emit(plan.events, context=context)

        # 14. Audit
        post_hash = tx_result.post_state_hash if tx_result else pre_hash
        target_ids: list[str] = []
        if hasattr(args, "file_id"):
            target_ids.append(getattr(args, "file_id"))
        if hasattr(args, "resource_id"):
            target_ids.append(getattr(args, "resource_id"))

        audit_id = _emit_audit(
            "success", pre_hash, post_hash, target_ids, event_ids, False,
            policy_decision=decision_str, rollback_ref=rollback_token,
        )

        # 15. Response-only failure
        should_fail, profile = dependencies.failure_model.should_fail(
            tool_id_str, "response_only", context.seed, context.step
        )
        if should_fail and profile and profile.failure_type == "false_success":
            # Return success=False to agent but state is actually committed
            return new_state, ToolExecutionResult(
                tool_call_id=context.tool_call_id, tool_id=tool_id_str,
                success=False,
                error=ToolError.transient("Operation status uncertain"),
                state_diff=tx_result.state_diff if tx_result else _empty_diff,
                events_emitted=event_ids, audit_ids=[audit_id],
                pre_state_hash=pre_hash, post_state_hash=post_hash,
                authorization_decision=decision_str, rollback_token=rollback_token,
                internal_truth={"actual_success": True},
            )

        # 16. Store idempotency result
        if idem_key and self.specification.idempotent:
            dependencies.idempotency_store.store(
                idem_key, context.actor_id, tool_id_str, raw_arguments,
                {"success": True, "output": read_output},
            )

        return new_state, ToolExecutionResult(
            tool_call_id=context.tool_call_id, tool_id=tool_id_str,
            success=True, output=read_output,
            state_diff=tx_result.state_diff if tx_result else _empty_diff,
            events_emitted=event_ids, audit_ids=[audit_id],
            pre_state_hash=pre_hash, post_state_hash=post_hash,
            authorization_decision=decision_str, rollback_token=rollback_token,
        )
