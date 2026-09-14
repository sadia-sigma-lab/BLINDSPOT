"""Software-ops domain-specific schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.resource import ResourceRecord


class PipelineRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    pipeline_id: str
    name: str
    branch: str = "main"
    status: Literal["idle", "running", "passed", "failed", "blocked"] = "idle"
    last_run_at: datetime | None = None
    deployment_target: str = "staging"
    requires_approval: bool = False


class SecretRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    secret_id: str
    secret_type: Literal["api_key", "db_password", "signing_key", "token"]
    value_ref: str  # Always a reference, never a plain value
    rotated_at: datetime | None = None
    expiry: datetime | None = None
    accessed_by: list[str] = Field(default_factory=list)


class DeploymentRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    deployment_id: str
    pipeline_id: str
    environment: Literal["dev", "staging", "prod", "canary"]
    status: Literal["pending", "approved", "running", "succeeded", "failed", "rolled_back"]
    approved_by: list[str] = Field(default_factory=list)
    rollback_target: str | None = None


class IncidentRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    incident_id: str
    severity: Literal["p0", "p1", "p2", "p3"]
    title: str
    status: Literal["open", "acknowledged", "mitigating", "resolved"]
    assigned_to: list[str] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
