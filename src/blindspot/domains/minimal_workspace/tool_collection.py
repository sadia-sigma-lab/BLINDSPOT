"""Build a WorldState from a DomainStateBundle for tool execution."""

from __future__ import annotations

import uuid
from pathlib import Path

from blindspot.core.state import WorldState
from blindspot.domains.minimal_workspace.state_builder import DomainStateBundle


def bundle_to_world_state(
    bundle: DomainStateBundle,
    seed: int = 42,
    episode_id: str | None = None,
    session_id: str | None = None,
    raw_resources: dict | None = None,
) -> WorldState:
    """Serialize a DomainStateBundle into a WorldState suitable for tool execution."""
    public = {}

    public["users"] = {uid: u.model_dump() for uid, u in bundle.users.items()}
    public["organizations"] = {oid: o.model_dump() for oid, o in bundle.organizations.items()}
    # Use raw_resources (full fixture JSON) when available to preserve domain-specific fields
    if raw_resources is not None:
        public["resources"] = raw_resources
    else:
        public["resources"] = {rid: r.model_dump() for rid, r in bundle.resources.items()}
    public["permissions"] = {pid: p.model_dump() for pid, p in bundle.permissions.items()}
    public["approvals"] = {aid: a.model_dump() for aid, a in bundle.approvals.items()}
    public["messages"] = {mid: m.model_dump() for mid, m in bundle.messages.items()}
    public["policies"] = {polid: pol.model_dump() for polid, pol in bundle.policies.items()}
    public["events"] = {eid: e.model_dump() for eid, e in bundle.events.items()}
    public["memory"] = {mid: m.model_dump() for mid, m in bundle.memory.items()}

    return WorldState(
        schema_version="1.0.0",
        episode_id=episode_id or str(uuid.uuid4()),
        step=0,
        session_id=session_id or str(uuid.uuid4()),
        random_seed=seed,
        public=public,
        private={},
        hidden=bundle.hidden_data,
        audit_log=[],
    )


def load_workspace_state(seed: int = 42) -> WorldState:
    """Load the minimal workspace fixture and return a WorldState."""
    import json
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBuilder
    import blindspot.domains.minimal_workspace.validators  # noqa: register invariants

    fixture_dir = Path(__file__).parent / "fixtures"
    manifest_path = fixture_dir / "manifest.yaml"
    builder = DomainStateBuilder()
    bundle, report = builder.build(manifest_path, seed=seed, strict=True)
    if not report.valid:
        errors = [i.message for i in report.errors()]
        raise RuntimeError(f"Fixture validation failed: {errors}")

    # Load raw resources to preserve domain-specific fields (shared_with, content, name)
    raw_resources_path = fixture_dir / "files.json"
    raw_resources: dict | None = None
    if raw_resources_path.exists():
        records = json.loads(raw_resources_path.read_text())
        raw_resources = {r["entity_id"]: r for r in records}

    return bundle_to_world_state(bundle, seed=seed, raw_resources=raw_resources)


def load_workspace_state_v2(seed: int = 42) -> WorldState:
    """Load the minimal workspace v2 fixture (richer: 30 files, injection messages, more users)."""
    import json
    from blindspot.domains.minimal_workspace.state_builder import DomainStateBuilder
    import blindspot.domains.minimal_workspace.validators  # noqa: register invariants

    fixture_dir = Path(__file__).parent / "fixtures_v2"
    manifest_path = fixture_dir / "manifest.yaml"
    builder = DomainStateBuilder()
    bundle, report = builder.build(manifest_path, seed=seed, strict=True)
    if not report.valid:
        errors = [i.message for i in report.errors()]
        raise RuntimeError(f"Fixture v2 validation failed: {errors}")

    raw_resources_path = fixture_dir / "files.json"
    raw_resources: dict | None = None
    if raw_resources_path.exists():
        records = json.loads(raw_resources_path.read_text())
        raw_resources = {r["entity_id"]: r for r in records}

    return bundle_to_world_state(bundle, seed=seed, raw_resources=raw_resources)
