"""Unit tests for audit record emission."""

from blindspot.tools.audit import InMemoryAuditSink, build_audit_record
from blindspot.tools.runtime import make_context


def test_success_recorded():
    sink = InMemoryAuditSink()
    ctx = make_context("user_alice", step=0, seed=42)
    record = build_audit_record(ctx, "core:list-files@1.0.0", {}, [], "success",
                                 None, None, [])
    aid = sink.append(record)
    assert aid == record.entity_id
    assert len(sink.list_for_episode("ep")) == 1


def test_failure_recorded():
    sink = InMemoryAuditSink()
    ctx = make_context("user_alice", step=0, seed=42)
    record = build_audit_record(ctx, "core:share-file@1.0.0", {"file_id": "f1"},
                                 ["f1"], "failure", "deny", None, [],
                                 error_code="AUTHORIZATION_DENIED")
    sink.append(record)
    records = sink.list_for_episode("ep")
    assert records[0].metadata["error_code"] == "AUTHORIZATION_DENIED"


def test_args_are_hashed_not_plaintext():
    sink = InMemoryAuditSink()
    ctx = make_context("user_alice", step=0, seed=42)
    sensitive_args = {"password": "super_secret_123", "file_id": "f1"}
    record = build_audit_record(ctx, "core:read-file@1.0.0", sensitive_args,
                                 ["f1"], "success", None, None, [])
    # args_hash should not contain the sensitive value
    args_hash = record.metadata.get("args_hash", "")
    assert "super_secret_123" not in str(args_hash)
    assert len(args_hash) > 0


def test_hidden_data_absent():
    sink = InMemoryAuditSink()
    ctx = make_context("user_alice", step=0, seed=42)
    record = build_audit_record(ctx, "core:read-file@1.0.0", {},
                                 ["f1"], "success", None, None, [])
    record_str = str(record.model_dump())
    assert "grading" not in record_str
    assert "attack_state" not in record_str
