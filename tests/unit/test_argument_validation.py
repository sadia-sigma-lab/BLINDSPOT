"""Unit tests for argument validation."""

import pytest
from pydantic import BaseModel, ConfigDict
from blindspot.tools.arguments import validate_arguments, pydantic_to_tool_schema


class SampleArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_id: str
    count: int = 1


def test_valid_args():
    obj, err = validate_arguments(SampleArgs, {"file_id": "f1"})
    assert err is None
    assert obj.file_id == "f1"


def test_missing_required_field():
    obj, err = validate_arguments(SampleArgs, {})
    assert obj is None
    assert err is not None
    assert err.category == "validation"


def test_unknown_field_rejected():
    obj, err = validate_arguments(SampleArgs, {"file_id": "f1", "surprise": True})
    assert obj is None
    assert err is not None


def test_wrong_type_rejected():
    obj, err = validate_arguments(SampleArgs, {"file_id": "f1", "count": "not-an-int"})
    assert obj is None
    assert err is not None


def test_schema_generation():
    schema = pydantic_to_tool_schema(SampleArgs, name="sample", description="A test tool")
    assert schema["name"] == "sample"
    assert "file_id" in schema["parameters"]["properties"]
