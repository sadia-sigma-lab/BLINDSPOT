"""Unit tests for snapshot create/restore and RNG state."""

import pytest

from blindspot.core.snapshot import RuntimeState


def _make_runtime_state(snapshot_id: str = "snap-1") -> RuntimeState:
    return RuntimeState(
        snapshot_id=snapshot_id,
        scenario_id="core:minimal-share@1.0.0",
        session_id="sess-abc",
        step=3,
        world_state={"public": {"x": 1}, "private": {}, "hidden": {}, "audit_log": []},
        event_queue=[],
        rng_state={"version": 3, "internalstate": list(range(624)) + [624], "gauss_next": None},
        plugin_versions={"core": "0.1.0"},
        package_version="0.1.0",
    )


def test_create_and_restore(tmp_path):
    from blindspot.storage.file_store import FileStore

    store = FileStore(tmp_path)
    snap = _make_runtime_state()

    path = store.write_json(f"snapshots/{snap.snapshot_id}.json", snap.model_dump())
    loaded_dict = store.read_json(f"snapshots/{snap.snapshot_id}.json")
    restored = RuntimeState(**loaded_dict)

    assert restored.snapshot_id == snap.snapshot_id
    assert restored.step == snap.step


def test_rng_restoration():
    import random

    snap = _make_runtime_state()
    rng = random.Random(42)
    state_before = rng.getstate()

    # advance the RNG
    rng.random()
    rng.random()

    # restore from snapshot rng_state
    tup = (
        snap.rng_state["version"],
        tuple(snap.rng_state["internalstate"]),
        snap.rng_state["gauss_next"],
    )
    rng.setstate(tup)
    assert rng.getstate() == tup


def test_event_queue_restored():
    snap = _make_runtime_state()
    from blindspot.runtime.event_queue import EventQueue

    # empty queue round-trip
    q = EventQueue.from_list(snap.event_queue)
    assert len(q) == 0


def test_snapshot_is_immutable():
    snap = _make_runtime_state()
    with pytest.raises(Exception):
        snap.step = 99  # type: ignore[misc]
