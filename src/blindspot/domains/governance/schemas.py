"""Governance domain schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from blindspot.data_model.resource import ResourceRecord


class DeploymentConfigRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    config_name: str
    environment: Literal["dev", "staging", "prod", "canary"]
    human_review_required: bool = True
    min_approvers: int = 1
    approver_ids: list[str] = Field(default_factory=list)
    automated_checks: list[str] = Field(default_factory=list)
    blocked: bool = False


class ApprovalMatrixRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    matrix_name: str
    quorum_required: int = 2
    approver_ids: list[str] = Field(default_factory=list)
    scope: str = "default"
    active: bool = True


class MonitoringRuleRecord(ResourceRecord):
    model_config = ConfigDict(frozen=True)
    rule_name: str
    metric: str
    threshold: float
    floor_threshold: float  # minimum allowed threshold
    alert_severity: Literal["info", "warning", "critical"]
    enabled: bool = True
    notification_channels: list[str] = Field(default_factory=list)
