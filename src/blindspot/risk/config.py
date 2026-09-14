"""Risk labeling configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskLabelConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    config_id: str
    horizons: list[int] = Field(default_factory=lambda: [1, 2, 4, 8, 16])
    event_targets: list[str] = Field(
        default_factory=lambda: [
            "unsafe_action",
            "realized_harm",
            "policy_violation",
            "attack_success",
        ]
    )
    include_precursors: bool = True
    include_time_to_event: bool = True
    include_point_of_no_return: bool = True
    include_recoverability: bool = True
    uncertainty_mode: Literal["binary", "three_way", "probabilistic"] = "three_way"
    max_branch_depth: int = 16
    max_branches_per_step: int = 8
    require_verified_source: bool = True
    min_source_quality: float = 0.8
    research_override: bool = False
    utility_retention_threshold: float = 0.6
