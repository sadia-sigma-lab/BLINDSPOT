"""Unit tests for idempotency store."""

import pytest
from blindspot.tools.idempotency import IdempotencyStore


def test_same_request_returns_stored():
    store = IdempotencyStore()
    args = {"file_id": "f1", "target_id": "x@example.com"}
    store.store("key1", "user_alice", "core:share-file@1.0.0", args, {"success": True})
    record, err = store.check("key1", "user_alice", "core:share-file@1.0.0", args)
    assert err is None
    assert record is not None
    assert record.result_snapshot["success"] is True


def test_different_args_with_same_key_conflict():
    store = IdempotencyStore()
    store.store("key1", "user_alice", "core:share-file@1.0.0",
                {"file_id": "f1"}, {"success": True})
    _, err = store.check("key1", "user_alice", "core:share-file@1.0.0",
                          {"file_id": "f2"})  # different
    assert err is not None
    assert err.category == "conflict"


def test_no_prior_record_returns_none():
    store = IdempotencyStore()
    record, err = store.check("nonexistent", "user_alice", "tool", {})
    assert record is None
    assert err is None
