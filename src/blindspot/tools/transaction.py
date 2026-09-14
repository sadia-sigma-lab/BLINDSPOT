"""Atomic transaction manager for tool state mutations."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blindspot.core.state import WorldState
from blindspot.core.state_diff import StateDiff, StateMutation
from blindspot.tools.mutation import MutationOperation, MutationPlan
from blindspot.validators.reports import ValidationReport, ValidationIssue


class TransactionResult(BaseModel):
    """Result of attempting to commit a MutationPlan."""

    model_config = ConfigDict(frozen=True)

    committed: bool
    state_diff: StateDiff = Field(default_factory=lambda: StateDiff(mutations=[]))
    pre_state_hash: str = ""
    post_state_hash: str = ""
    rollback_token: str | None = None
    validation_report: ValidationReport = Field(
        default_factory=lambda: ValidationReport(
            valid=True, issues=[], checked_files=0, checked_entities=0, fixture_id=""
        )
    )


def _hash_public(public: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(public, sort_keys=True, default=str).encode()
    ).hexdigest()


class TransactionManager:
    """Stages, validates, and atomically commits mutation plans."""

    def commit(
        self,
        state: WorldState,
        plan: MutationPlan,
        write_scopes: list[str],
        domain_bundle: Any | None = None,
    ) -> tuple[WorldState, TransactionResult]:
        """Apply plan to state atomically; return (new_state, result)."""
        from blindspot.tools.state_view import _ALWAYS_HIDDEN

        pre_hash = _hash_public(state.public)

        # Validate write scopes
        issues: list[ValidationIssue] = []
        for op in plan.operations:
            if op.collection in _ALWAYS_HIDDEN:
                issues.append(ValidationIssue(
                    severity="error", code="SCOPE_VIOLATION",
                    message=f"Write to hidden collection {op.collection!r} is forbidden",
                    collection=op.collection,
                ))
            elif op.collection not in write_scopes:
                issues.append(ValidationIssue(
                    severity="error", code="SCOPE_VIOLATION",
                    message=f"Collection {op.collection!r} not in write scopes",
                    collection=op.collection,
                ))

        if issues:
            report = ValidationReport(
                valid=False, issues=issues, checked_files=0,
                checked_entities=len(plan.operations), fixture_id=""
            )
            return state, TransactionResult(committed=False, pre_state_hash=pre_hash,
                                             post_state_hash=pre_hash, validation_report=report)

        # Stage mutations on a deep copy
        staged_public = copy.deepcopy(state.public)
        mutations: list[StateMutation] = []

        for op in plan.operations:
            coll = staged_public.setdefault(op.collection, {})
            if op.operation == "create":
                if op.entity_id in coll:
                    issues.append(ValidationIssue(
                        severity="error", code="ENTITY_EXISTS",
                        message=f"{op.collection}/{op.entity_id} already exists",
                        collection=op.collection, entity_id=op.entity_id,
                    ))
                    continue
                coll[op.entity_id] = copy.deepcopy(op.after or {})
                mutations.append(StateMutation(
                    path=f"public.{op.collection}.{op.entity_id}",
                    operation="add", after=op.after,
                ))
            elif op.operation == "update":
                before = copy.deepcopy(coll.get(op.entity_id, {}))
                merged = {**before, **(op.after or {})}
                coll[op.entity_id] = merged
                mutations.append(StateMutation(
                    path=f"public.{op.collection}.{op.entity_id}",
                    operation="replace", before=before, after=merged,
                ))
            elif op.operation == "delete":
                before = copy.deepcopy(coll.pop(op.entity_id, None))
                mutations.append(StateMutation(
                    path=f"public.{op.collection}.{op.entity_id}",
                    operation="remove", before=before,
                ))

        if issues:
            report = ValidationReport(
                valid=False, issues=issues, checked_files=0,
                checked_entities=len(plan.operations), fixture_id=""
            )
            return state, TransactionResult(committed=False, pre_state_hash=pre_hash,
                                             post_state_hash=pre_hash, validation_report=report)

        # Commit: build new state
        new_state = WorldState(
            schema_version=state.schema_version,
            episode_id=state.episode_id,
            step=state.step,
            session_id=state.session_id,
            random_seed=state.random_seed,
            public=staged_public,
            private=state.private,
            hidden=state.hidden,
            audit_log=state.audit_log,
        )
        post_hash = _hash_public(staged_public)
        diff = StateDiff(mutations=mutations)

        report = ValidationReport(
            valid=True, issues=[], checked_files=0,
            checked_entities=len(plan.operations), fixture_id=""
        )
        return new_state, TransactionResult(
            committed=True, state_diff=diff,
            pre_state_hash=pre_hash, post_state_hash=post_hash,
            validation_report=report,
        )
