"""Execution context and runtime dependency container."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from blindspot.domains.minimal_workspace.policies import AuthorizationEngine
    from blindspot.runtime.event_queue import EventQueue
    from blindspot.tools.audit import AuditSink
    from blindspot.tools.idempotency import IdempotencyStore
    from blindspot.tools.failure_model import ToolFailureModel
    from blindspot.tools.transaction import TransactionManager
    from blindspot.tools.rollback import RollbackManager
    from blindspot.data_model.visibility import StateProjector


class ToolExecutionContext(BaseModel):
    """Immutable per-call execution context passed to every tool."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    episode_id: str
    session_id: str
    scenario_id: str
    domain_id: str
    actor_id: str
    step: int
    seed: int
    current_time: datetime
    tool_call_id: str
    idempotency_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@dataclass
class ToolRuntimeDependencies:
    """All external services the tool runtime requires."""

    authorization_engine: "AuthorizationEngine"
    transaction_manager: "TransactionManager"
    rollback_manager: "RollbackManager"
    event_queue: "EventQueue"
    audit_sink: "AuditSink"
    idempotency_store: "IdempotencyStore"
    failure_model: "ToolFailureModel"
    visibility_projector: "StateProjector"
    extra: dict[str, Any] = field(default_factory=dict)
