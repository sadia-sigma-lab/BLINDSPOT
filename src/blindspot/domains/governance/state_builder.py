"""Governance domain state builder."""

from __future__ import annotations

import uuid
from pathlib import Path

from blindspot.core.state import WorldState
from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle, DomainStateBuilder


def bundle_to_governance_state(bundle: DomainStateBundle, seed: int = 42) -> WorldState:
    public: dict = {}
    public["users"] = {uid: u.model_dump() for uid, u in bundle.users.items()}
    public["resources"] = {rid: r.model_dump() for rid, r in bundle.resources.items()}
    public["permissions"] = {pid: p.model_dump() for pid, p in bundle.permissions.items()}
    public["approvals"] = {aid: a.model_dump() for aid, a in bundle.approvals.items()}
    public["policies"] = {pid: pol.model_dump() for pid, pol in bundle.policies.items()}
    for k, v in bundle.domain_data.items():
        public[k] = v
    return WorldState(
        schema_version="1.0.0",
        episode_id=str(uuid.uuid4()),
        step=0,
        session_id=str(uuid.uuid4()),
        random_seed=seed,
        public=public,
        private={},
        hidden=bundle.hidden_data,
        audit_log=[],
    )


def load_governance_state(seed: int = 42) -> WorldState:
    import blindspot.domains.governance.validators  # register invariants
    manifest_path = Path(__file__).parent / "fixtures" / "manifest.yaml"
    builder = DomainStateBuilder()
    bundle, report = builder.build(manifest_path, seed=seed, strict=True)
    if not report.valid:
        errors = [i.message for i in report.errors()]
        raise RuntimeError(f"Governance fixture validation failed: {errors}")
    return bundle_to_governance_state(bundle, seed=seed)
