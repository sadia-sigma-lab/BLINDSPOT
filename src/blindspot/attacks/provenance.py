"""Attack provenance tracking."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AttackProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)
    attack_instance_id: str
    attack_id: str
    scenario_id: str
    run_id: str
    seed: int
    config_hash: str
    author: str = ""
    source_package: str = ""
    version: str = ""
    license: str = "Apache-2.0"
