"""Finance domain state builder."""
from __future__ import annotations
import json
import uuid
from pathlib import Path

from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle, DomainStateBuilder
from blindspot.core.state import WorldState


def bundle_to_finance_state(bundle: DomainStateBundle, seed: int = 42) -> WorldState:
    public = {}
    public["users"] = {uid: u.model_dump() for uid, u in bundle.users.items()}
    public["resources"] = {}
    for rid, r in bundle.resources.items():
        try:
            public["resources"][rid] = r.model_dump()
        except Exception:
            pass
    public["permissions"] = {pid: p.model_dump() for pid, p in bundle.permissions.items()}
    public["approvals"] = {aid: a.model_dump() for aid, a in bundle.approvals.items()}
    public["policies"] = {polid: pol.model_dump() for polid, pol in bundle.policies.items()}
    # Also include domain_data for accounts, payments, pii.
    # Domain data is stored as lists (from JSON arrays); convert to dicts keyed by entity_id
    # so tools can do dict lookups (e.g. view.get_collection("accounts")).
    for k, v in bundle.domain_data.items():
        if isinstance(v, list):
            public[k] = {
                item["entity_id"]: item
                for item in v
                if isinstance(item, dict) and "entity_id" in item
            }
        else:
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


def load_finance_state(seed: int = 42) -> WorldState:
    import blindspot.domains.finance.validators  # register invariants
    manifest_path = Path(__file__).parent / "fixtures" / "manifest.yaml"
    builder = DomainStateBuilder()
    bundle, report = builder.build(manifest_path, seed=seed, strict=True)
    if not report.valid:
        errors = [i.message for i in report.errors()]
        raise RuntimeError(f"Finance fixture validation failed: {errors}")
    return bundle_to_finance_state(bundle, seed=seed)
