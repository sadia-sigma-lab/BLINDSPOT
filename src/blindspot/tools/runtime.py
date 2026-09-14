"""Tool runtime — assembles dependencies and dispatches via the router."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from blindspot.core.state import WorldState
from blindspot.domains.minimal_workspace.policies import AuthorizationEngine
from blindspot.data_model.visibility import StateProjector
from blindspot.runtime.event_queue import EventQueue
from blindspot.tools.audit import InMemoryAuditSink
from blindspot.tools.context import ToolExecutionContext, ToolRuntimeDependencies
from blindspot.tools.failure_model import ToolFailureModel
from blindspot.tools.idempotency import IdempotencyStore
from blindspot.tools.rollback import RollbackManager
from blindspot.tools.router import ToolRouter
from blindspot.tools.transaction import TransactionManager


def build_default_dependencies(event_queue: EventQueue | None = None) -> ToolRuntimeDependencies:
    """Create a full dependency set with sensible defaults."""
    return ToolRuntimeDependencies(
        authorization_engine=AuthorizationEngine(),
        transaction_manager=TransactionManager(),
        rollback_manager=RollbackManager(),
        event_queue=event_queue or EventQueue(),
        audit_sink=InMemoryAuditSink(),
        idempotency_store=IdempotencyStore(),
        failure_model=ToolFailureModel.null(),
        visibility_projector=StateProjector(),
    )


def make_context(
    actor_id: str,
    step: int,
    seed: int,
    tool_call_id: str | None = None,
    episode_id: str = "ep",
    session_id: str = "sess",
    scenario_id: str = "core:minimal-share@1.0.0",
    domain_id: str = "core:minimal-workspace@1.0.0",
    run_id: str = "run-default",
    current_time: datetime | None = None,
    idempotency_key: str | None = None,
) -> ToolExecutionContext:
    import uuid
    return ToolExecutionContext(
        run_id=run_id,
        episode_id=episode_id,
        session_id=session_id,
        scenario_id=scenario_id,
        domain_id=domain_id,
        actor_id=actor_id,
        step=step,
        seed=seed,
        current_time=current_time or datetime(2026, 6, 1, tzinfo=timezone.utc),
        tool_call_id=tool_call_id or str(uuid.uuid4()),
        idempotency_key=idempotency_key,
    )
