"""Unit tests for StateDiff and apply_diff."""

import pytest

from blindspot.core.state_diff import StateDiff, StateMutation, apply_diff


def _base() -> dict:
    return {"public": {"files": {"f1": {"name": "a.txt", "shared_with": []}}}, "private": {}}


def test_add_mutation() -> None:
    diff = StateDiff(mutations=[StateMutation(path="public.new_key", operation="add", after="v")])
    result = apply_diff(_base(), diff)
    assert result["public"]["new_key"] == "v"


def test_replace_mutation() -> None:
    diff = StateDiff(
        mutations=[
            StateMutation(
                path="public.files.f1.name",
                operation="replace",
                before="a.txt",
                after="b.txt",
            )
        ]
    )
    result = apply_diff(_base(), diff)
    assert result["public"]["files"]["f1"]["name"] == "b.txt"


def test_remove_mutation() -> None:
    diff = StateDiff(
        mutations=[StateMutation(path="public.files.f1.name", operation="remove", before="a.txt")]
    )
    result = apply_diff(_base(), diff)
    assert "name" not in result["public"]["files"]["f1"]


def test_empty_diff_noop() -> None:
    diff = StateDiff(mutations=[])
    original = _base()
    result = apply_diff(original, diff)
    assert result == original


def test_invalid_path_raises_on_replace() -> None:
    diff = StateDiff(
        mutations=[StateMutation(path="public.nonexistent.x", operation="replace", after="v")]
    )
    from blindspot.exceptions import StateError
    with pytest.raises(StateError):
        apply_diff(_base(), diff)


def test_state_hash_changes_after_apply() -> None:
    import hashlib, json
    state = _base()
    before_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    diff = StateDiff(
        mutations=[StateMutation(path="public.x", operation="add", after="new")]
    )
    after = apply_diff(state, diff)
    after_hash = hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest()
    assert before_hash != after_hash


def test_inverse_interface_exists() -> None:
    diff = StateDiff(
        mutations=[StateMutation(path="public.x", operation="add", after="v")]
    )
    inv = diff.inverse()
    assert len(inv.mutations) == 1
    assert inv.mutations[0].operation == "remove"


def test_is_empty() -> None:
    assert StateDiff(mutations=[]).is_empty
    assert not StateDiff(mutations=[StateMutation(path="x", operation="add", after=1)]).is_empty
